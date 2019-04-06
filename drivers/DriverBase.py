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
    def __init__(self, id, args):
        self._id = id
        self._args = args
    def __str__(self):
        return 'Event({}, {}, {})'.format(self._id, self._args[0], self._args[1])
    @property
    def id(self):
        return self._id
    @property
    def args(self):
        return self._args[0]
    @property
    def kwargs(self):
        return self._args[1]

class DriverThunk():
    def __init__(self, dispatcher, event_name, id, event_queue):
        super().__init__()
        self._id = id
        self._event_queue = event_queue
        dispatcher_arg = { event_name: self.thunk }
        dispatcher.bind(**dispatcher_arg)
    def thunk(self, *args):
        event = DriverEvent(self._id, args)
        self._event_queue.put(event)
        return True

class DriverBase(Thread, Dispatcher):
    EVENT_STOP_NOW = 'stop_now'

    def __init__(self, name, config, loader, id):
        self._parent = default_driver_parent
        self._name = name
        self.config = config
        self.loader = loader
        self.id = id
        self._event_queue = queue.Queue()
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

    def find_driver_by_event(self, event_name):
        return self._parent.find_driver_by_event(event_name, self)

    def find_driver_by_name(self, driver_name):
        return self._parent.find_driver_by_name(driver_name, self)

    def getDriver(self, driver_name, controller=None):
        driver = self.loader.getDriver(driver_name, controller)
        if driver == None:
            raise RequiredDriverException(driver_name)
        return driver  

    def subscribe(self, driver_name, event_name, id, raise_on_not_found=True):
        if driver_name is None:
            partner = self.find_driver_by_event(event_name)
            if partner is None:
                if raise_on_not_found:
                    raise RequiredEventException(event_name)
                else:
                    return False
        else:
            partner = self.find_driver_by_name(driver_name)
            if partner is None:
                if raise_on_not_found:
                    raise RequiredDriverException(driver_name)
                else:
                    return False
        thunk = DriverThunk(partner, event_name, id, self._event_queue)
        self._event_thunks.append(thunk)
        return True

    def publish(self, event_name, *args, **kwargs):
        return self.emit(event_name, args, kwargs)

    def ok_to_start(self):
        return self._ok_to_start

    #fix
    #def revoke(self):

    def get(self, block=True, timeout=None):
        # fix: At some point _event_queue.task_done() should be called.
        return self._event_queue.get(block=block, timeout=timeout)

    def setup(self):
        self.subscribe(None, DriverBase.EVENT_STOP_NOW, self._stop_now, False)
        return False  # rmv

    def startup(self):
        self._keep_running = self._ok_to_start

    def loop(self):
        return False

    def _stop_now(self, event):
        self._keep_running = False

    def shutdown(self):
        pass

    def teardown(self):
        # fix: Teardown is currently not used.  This method is the inverse of
        # setup.  Whatever is down in setup should be undone in teardown.  If
        # this method is ever brought into play it will be called in the same
        # basic fashion as setup.
        pass

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

class DriverBaseOld(DriverBase):
    def __init__(self, config, loader, id):
        # fix: Loader needs to become Parent
        super().__init__(get_next_name(), config, loader, id)

