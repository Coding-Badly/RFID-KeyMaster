"""=============================================================================

  DriverBase for RFID-KeyMaster.  DriverBase is a base class for all run-time
  loadable drivers.  Each DriverBase is also a Thread allowing it to block
  without interfering with other parts of the application.  DriverBase provides
  three services: 1. Connection to configuration data and a parent; 2. Find
  siblings so drivers can interact directly with each other; 3. Turn all
  unexpected exceptions into a clean exit.
  
  ----------------------------------------------------------------------------

  Copyright 2019 Mike Cole (aka @Draco, MikeColeGuru)
  Copyright 2019 Brian Cook (aka @Brian, Coding-Badly)

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

============================================================================="""
from collections import OrderedDict
from threading import Thread
from exceptions.RequiredDriverException import RequiredDriverException
from exceptions.RequiredEventException import RequiredEventException
import heapq
import logging
import os
from pydispatch import Dispatcher
import queue
import selectors
from time import monotonic as time

logger = logging.getLogger(__name__)

next_name_index = 1

def get_next_name():
    global next_name_index
    rv = 'whatever #{}'.format(next_name_index)
    next_name_index += 1
    return rv

class FauxDriverParent():
    def find_driver_by_event(self, event_name, skip=None):
        return None
    def find_driver_by_name(self, driver_name, skip=None):
        return None

default_driver_parent = FauxDriverParent()

class DriverGroup(OrderedDict):
    def __init__(self, name=None):
        super().__init__()
        self._parent = None
        self._name = name if name else get_next_name()
        self._startable = list()

    @property
    def name(self):
        return self._name

    def add(self, driver_or_group):
        assert (driver_or_group._parent == default_driver_parent) \
                or (driver_or_group._parent is None)
        self[driver_or_group.name] = driver_or_group
        driver_or_group._parent = self
        return driver_or_group

    def emits_event(self, event_name):
        return False

    def has_values(self):
        return True

    def find_driver_by_event(self, event_name, skip=None):
        # Breadth-first search down then working up.
        heap = list()
        anchor = self
        order = 1
        # fix? The while loop probably needs to also continue if heap is not
        # empty.
        while anchor is not None:
            heapq.heappush(heap, (1, order, anchor))
            order += 1
            while heap:
                priority, _, current = heapq.heappop(heap)
                priority += 1
                if current.emits_event(event_name):
                    return current
                if current.has_values():
                    for child in current.values():
                        if child != skip:
                            heapq.heappush(heap, (priority, order, child))
                            order += 1
            skip = anchor
            anchor = anchor._parent

    def find_driver_by_name(self, driver_name, skip=None):
        # Short-circuit.  Most queries should stop here.
        rv = self.get(driver_name, None)
        if rv is not None:
            return rv
        # Breadth-first search down then working up.
        heap = list()
        anchor = self
        order = 1
        # fix? The while loop probably needs to also continue if heap is not
        # empty.
        while anchor is not None:
            heapq.heappush(heap, (1, order, anchor))
            order += 1
            while heap:
                priority, _, current = heapq.heappop(heap)
                priority += 1
                rv = current.get(driver_name, None)
                if rv is not None:
                    return rv
                for child in current.values():
                    # isinstance(child, DriverGroup) could be used instead of
                    # child.has_values().  has_values allows classes other
                    # than DriverGroup to participate.
                    if (child != skip) and child.has_values(): 
                        heapq.heappush(heap, (priority, order, child))
                        order += 1
            skip = anchor
            anchor = anchor._parent
        if driver_name == self.name:
            return self
        return None

    def ok_to_start(self):
        for driver_or_group in self.values():
            if not driver_or_group.ok_to_start():
                return False
        return True

    def setup(self):
        # fix? Do something with the return values?
        # fix? Fail to run if any return False?
        self._startable.clear()
        for driver_or_group in self.values():
            driver_or_group.setup()
            if driver_or_group.ok_to_start():
                self._startable.append(driver_or_group)

    def start(self):
        for driver_or_group in self._startable:
            driver_or_group.start()
        self._startable.clear()

    def teardown(self):
        for driver_or_group in self.values():
            driver_or_group.teardown()

class DriverEvent():
    def __init__(self, id, args, kwargs):
        self._id = id
        self._args = args
        self._kwargs = kwargs
    def __str__(self):
        return 'Event({}, {}, {})'.format(self._id, self._args, self._kwargs)
    @property
    def id(self):
        return self._id
    @property
    def args(self):
        return self._args
    @property
    def kwargs(self):
        return self._kwargs

class DriverThunk():
    def __init__(self, dispatcher, event_name, id, event_queue):
        super().__init__()
        self._id = id
        self._event_queue = event_queue
        dispatcher_arg = { event_name: self.thunk }
        dispatcher.bind(**dispatcher_arg)
    def thunk(self, *args, **kwargs):
        # rmv logger.info('DriverThunk.thunk: %s, %s', args, kwargs)
        event = DriverEvent(self._id, args, kwargs)
        self._event_queue.put(event)
        return True

class DriverQueue(queue.Queue):
    def setup(self):
        pass
    def teardown(self):
        pass

class DriverQueuePlusSelect():
    BYTE_ZERO = chr(0).encode()
    def __init__(self, *args, **kwargs):
        self._queue = queue.Queue(*args, **kwargs)
    def setup(self):
        self._selector = selectors.DefaultSelector()
        self._wake_pipe_read, self._wake_pipe_write = os.pipe()
        # rmv self.register = self._selector.register
        # rmv self.unregister = self._selector.unregister
        self.register(self._wake_pipe_read, selectors.EVENT_READ, None) # rmv EmptyPipe())
    def register(self, fileobj, events, data=None):
        # fix? Add support for auto-close?
        self._selector.register(fileobj, events, data)
    def unregister(self, fileobj):
        self._selector.unregister(fileobj)
    def put(self, item, block=True, timeout=None):
        self._queue.put(item, block, timeout)
        os.write(self._wake_pipe_write, DriverQueuePlusSelect.BYTE_ZERO)
    def get(self, block=True, timeout=None):
        select_timeout = 0
        tries = 0
        while True:
            tries += 1
            status = self._selector.select(timeout=select_timeout)
            if len(status) > 0:
                for row in status:
                    # row[0] is the SelectorKey.
                    # row[1] is an event mask.
                    key = row[0]
                    # Not our _wake_pipe_read?
                    if key.fd != self._wake_pipe_read:
                        # Found a file descriptor ready for I/O.  Wrap it and return.
                        return DriverEvent(key.data, (key, row[1]), {})
                    else:
                        # Just keep our wake pipe clear.
                        _ = os.read(self._wake_pipe_read, 1)  # aka key.fd
            try:
                event = self._queue.get_nowait()
                return event
            except queue.Empty:
                pass
            # There were no ready file descriptors and no queued events.
            # If we are not supposed to block then raise an exception.
            if not block:
                raise queue.Empty
            # Timeout?
            if tries > 1:
                if select_timeout is not None:
                    remaining = endtime - time()
                    if remaining <= 0.0:
                        raise queue.Empty
            # If we are supposed to block forever then adjust and loop.
            if timeout is None:
                select_timeout = None
                continue
            # Otherwise we are supposed to wait for timeout seconds.
            else:
                select_timeout = timeout
                if tries == 1:
                    endtime = time() + timeout
                continue
    def teardown(self):
        self.unregister(self._wake_pipe_read)
        for key in list(self._selector.get_map()):
            _ = self.unregister(key)
        self._selector.close()
        self._selector = None
        os.close(self._wake_pipe_write)
        self._wake_pipe_write = None
        os.close(self._wake_pipe_read)
        self._wake_pipe_read = None

class DriverBase(Thread, Dispatcher):
    EVENT_STOP_NOW = 'stop_now'

    def __init__(self, name, config, loader, id):
        self._parent = default_driver_parent
        self._name = name
        self.config = config
        self.loader = loader
        self.id = id
        # rmv self._event_queue = DriverQueue()
        self._event_thunks = list()
        # fix: Use the following instead of returning a Boolean from setup.
        self._ok_to_start = True
        super().__init__(name=name)

    @property
    def name(self):
        return self._name

    def emits_event(self, event_name):
        events = getattr(self, '_EVENTS_', None)
        if events is None:
            return False
        return event_name in events

    def has_values(self):
        return False

    def find_driver_by_event(self, event_name, skip_self=True):
        skip = self if skip_self else None
        return self._parent.find_driver_by_event(event_name, skip)

    def find_driver_by_name(self, driver_name, skip_self=True):
        skip = self if skip_self else None
        return self._parent.find_driver_by_name(driver_name, skip)

    def getDriver(self, driver_name, controller=None):
        driver = self.loader.getDriver(driver_name, controller)
        if driver == None:
            raise RequiredDriverException(driver_name)
        return driver  

    def subscribe(self, driver_name, event_name, id, raise_on_not_found=True, skip_self=True):
        if driver_name is None:
            partner = self.find_driver_by_event(event_name, skip_self)
            if partner is None:
                if raise_on_not_found:
                    raise RequiredEventException(event_name)
                else:
                    return False
        else:
            partner = self.find_driver_by_name(driver_name, skip_self)
            if partner is None:
                if raise_on_not_found:
                    raise RequiredDriverException(driver_name)
                else:
                    return False
        # rmv logger.info('self=%s, partner=%s, event_name=%s', self, partner, event_name)
        thunk = DriverThunk(partner, event_name, id, self._event_queue)
        self._event_thunks.append(thunk)
        return True

    def publish(self, event_name, *args, **kwargs):
        return self.emit(event_name, *args, **kwargs)

    #fix
    #def revoke(self):

    def ok_to_start(self):
        return self._ok_to_start

    def get(self, block=True, timeout=None):
        # fix: At some point _event_queue.task_done() should be called.
        return self._event_queue.get(block=block, timeout=timeout)

    def process_one(self, timeout=None):
        try:
            event = self._event_queue.get(block=True, timeout=timeout)
            event.id(*event.args, **event.kwargs)
            return True
        except queue.Empty:
            pass
        return False

    def _create_event_queue(self):
        return DriverQueue()

    def setup(self):
        self._event_queue = self._create_event_queue()
        self._event_queue.setup()
        self.subscribe(None, DriverBase.EVENT_STOP_NOW, self._stop_now, False, False)
        return False  # rmv

    def startup(self):
        self._keep_running = self._ok_to_start

    def loop(self):
        while self._keep_running:
            self.process_one()
        return False

    def _stop_now(self):
        self._keep_running = False

    def shutdown(self):
        pass

    def teardown(self):
        # fix: Teardown is currently not used.  This method is the inverse of
        # setup.  Whatever is down in setup should be undone in teardown.  If
        # this method is ever brought into play it will be called in the same
        # basic fashion as setup.
        self._event_queue.teardown()

    def run(self):
        try:
            self.startup()
            # rmv self.startup = True
            try:
                while self._keep_running:
                    if not self.loop():
                        self._keep_running = False
                    # rmv self.startup = False
            finally:
                self.shutdown()
        except Exception as e:
            # fix? Call a method on self about the exception?
            logging.error("Exception: %s" % str(e), exc_info=1)
            os._exit(42) # Make sure entire application exits

class DeathOfRats(DriverBase):
    _events_ = [DriverBase.EVENT_STOP_NOW]
    def stop_all(self):
        # rmv logger.info('DeathOfRats.stop_now...')
        self.publish(DriverBase.EVENT_STOP_NOW)
        # rmv logger.info('...DeathOfRats.stop_now')
    def shutdown(self):
        super().shutdown()
        self.publish(DriverBase.EVENT_STOP_NOW)

class DriverBaseOld(DriverBase):
    def __init__(self, config, loader, id):
        # fix: Loader needs to become Parent
        super().__init__(get_next_name(), config, loader, id)
    def loop(self):
        return False

