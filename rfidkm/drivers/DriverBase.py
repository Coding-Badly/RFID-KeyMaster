"""=============================================================================

  DriverBase for RFID-KeyMaster.  DriverBase is a base class for all run-time
  loadable drivers.  Each DriverBase is also a Thread allowing it to block
  without interfering with other parts of the application.  DriverBase provides
  three services: 1. Connection to configuration data and a parent; 2. Find
  siblings so drivers can interact directly with each other; 3. Turn all
  unexpected exceptions into a clean exit.

  DriverBase instances have a state.  The first state is "constructed".  This
  stated is implied from an instance being created.  A minimum amount of 
  initialization is performed so the instance is stable (but unusable).  
  Constructed happens from the primary thread.

  The next state is "initialized".  This state is entered when setup is
  called.  Initialized happens from the primary thread.  Typical activities
  include locating and connecting to partners.  Just enough should be done to
  make the instance ready to run.

  The next state is "running".  This state is entered when start_and_wait is
  called.  Each instance is expected to create a thread then continue running
  from that thread.  The start_and_wait method is called from the primary
  thread and blocks until the thread has indicated it is ready for business.

  When running is entered, the run method is called which calls startup, loop
  until _keep_running is False, then shutdown.

  The thread terminating leaves the DriverBase in a "terminated" state.
  Theoretically, it is possible to restart the thread transitioning to
  running.  At the time this was written that is neither tested nor needed.

  If teardown is called the DriverBase transitions back to constructed.

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
from collections import defaultdict, OrderedDict
import enum
import heapq
import logging
from operator import methodcaller
import os
import queue
import selectors
from threading import Thread, Event, Lock
from time import monotonic

from pydispatch import Dispatcher

from .signals import DriverSignals
from ..exceptions import DriverWontStartError, LeftOverEdgesError
from ..exceptions.RequiredDriverException import RequiredDriverException
from ..exceptions.RequiredEventException import RequiredEventException

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

class DriverBaseState(enum.IntEnum):
    FIRST = 1
    CONSTRUCTING = enum.auto()
    CONSTRUCTED = enum.auto()
    INITIALIZING = enum.auto()
    INITIALIZED = enum.auto()
    STARTING = enum.auto()
    STARTED = enum.auto()
    STOPPING = enum.auto()
    STOPPED = enum.auto()
    TEARINGDOWN = enum.auto()
    TORNDOWN = enum.auto()
    LAST = enum.auto()

CONFIGURATION_STATE = {DriverBaseState.CONSTRUCTING, DriverBaseState.CONSTRUCTED, DriverBaseState.INITIALIZING, DriverBaseState.INITIALIZED}
THREAD_ACTIVE_STATE = {DriverBaseState.STARTING, DriverBaseState.STARTED, DriverBaseState.STOPPING}

class DriverGroup(OrderedDict):
    def __init__(self, name=None):
        super().__init__()
        self._parent = None
        self._name = name if name else get_next_name()
        self._flattened = None
        self._in_start_order = None
        self._startable = list()

    @property
    def name(self):
        return self._name

    def add(self, driver_or_group):
        assert (driver_or_group._parent == default_driver_parent) \
                or (driver_or_group._parent is None)
        assert self._flattened is None
        assert self._in_start_order is None
        self[driver_or_group.name] = driver_or_group
        driver_or_group._parent = self
        return driver_or_group

    def emits_event(self, event_name):
        return False

    def has_values(self):
        return True

    def _flatten(self):
        stack = list()
        rover = iter(self.values())
        while True:
            try:
                current = next(rover)
                if current.has_values():
                    stack.append(rover)
                    rover = iter(current.values())
                else:
                    yield current
            except StopIteration:
                if stack:
                    rover = stack.pop()
                else:
                    break

    def flatten(self):
        return [item for item in self._flatten()]

    def _check_flattened(self):
        if self._flattened is None:
            self._flattened = self.flatten()
        return self._flattened

    def _check_in_start_order(self):
        if self._in_start_order is None:
            # Toplogical sort of the drivers by subscribe dependency.
            in_start_order = list()
            no_incoming_edge = set()
            d2s_edges = defaultdict(set)
            flattened = self._check_flattened()
            # fix? There is an unchecked assumption that len(flattened) > 0.
            for driver in flattened:
                if len(driver._start_before) == 0:
                    no_incoming_edge.add(driver)
                else:
                    for rover in driver._start_before:
                        d2s_edges[rover].add(driver)
            # If no_incoming_edge is empty we're stuffed.
            assert len(no_incoming_edge) > 0
            while no_incoming_edge:
                driver = no_incoming_edge.pop()
                in_start_order.append(driver)
                for src in d2s_edges[driver]:
                    src._start_before.remove(driver)
                    if len(src._start_before) == 0:
                        no_incoming_edge.add(src)
                del d2s_edges[driver]
            assert len(no_incoming_edge) == 0
            if len(d2s_edges) != 0:
                raise LeftOverEdgesError()
            # fix? Set all driver._start_before to None?
            self._in_start_order = in_start_order
        return self._in_start_order

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

    def setup(self):
        for driver in self._check_flattened():
            assert driver._driver_state == DriverBaseState.CONSTRUCTED
            driver._driver_state = DriverBaseState.INITIALIZING
            rv = driver.setup()
            assert rv is None
            driver._driver_state = DriverBaseState.INITIALIZED

    def start(self):
        drivers_in_start_order = self._check_in_start_order()
        not_ok_to_start = [driver for driver in drivers_in_start_order if not driver.ok_to_start()]
        if not_ok_to_start:
            raise DriverWontStartError(not_ok_to_start)
        for driver in drivers_in_start_order:
            assert driver._driver_state == DriverBaseState.INITIALIZED
            driver._driver_state = DriverBaseState.STARTING
            driver.start_and_wait()

    def teardown(self):
        for driver in self._check_flattened():
            assert driver._driver_state == DriverBaseState.STOPPED
            driver._driver_state = DriverBaseState.TEARINGDOWN
            driver.teardown()
            driver._driver_state = DriverBaseState.TORNDOWN

    def join(self):
        for driver in self._check_flattened():
            driver.join()
            driver._driver_state = DriverBaseState.STOPPED

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

class DriverTimelet():
    def __init__(self, payload, first_due):
        self._payload = payload
        self._when_due = first_due
        self._enabled = True
    def expired(self):
        return False
    @property
    def payload(self):
        return self._payload
    @property
    def when_due(self):
        return self._when_due
    def __lt__(self, other):
        return self._when_due < other._when_due
    def __le__(self, other):
        return self._when_due <= other._when_due
    def __gt__(self, other):
        return self._when_due > other._when_due
    def __ge__(self, other):
        return self._when_due >= other._when_due
    def __eq__(self, other):
        return self._when_due == other._when_due
    def __ne__(self, other):
        return self._when_due != other._when_due
    def disable(self):
        self._enabled = False

class DriverTimeletInterval(DriverTimelet):
    def __init__(self, payload, every, fire_now=False):
        if fire_now:
            first_due = monotonic()
        else:
            first_due = monotonic() + every
        super().__init__(payload, first_due)
        self._every = every
    def expired(self):
        self._when_due += self._every
        return True

class DriverThunk():
    def __init__(self, dispatcher, event_name, id, event_queue):
        super().__init__()
        self._id = id
        self._event_queue = event_queue
        dispatcher.bind1(event_name, self.thunk)
    def thunk(self, *args, **kwargs):
        event = DriverEvent(self._id, args, kwargs)
        self._event_queue.put(event)
        return True

class DriverQueue(queue.Queue):
    def _setup(self):
        pass
    def _teardown(self):
        pass

class DriverQueuePlusSelect():
    BYTE_ZERO = chr(0).encode()
    def __init__(self, *args, **kwargs):
        self._queue = queue.Queue(*args, **kwargs)
    def _setup(self):
        self._selector = selectors.DefaultSelector()
        self._wake_pipe_read, self._wake_pipe_write = os.pipe()
        self.register(self._wake_pipe_read, selectors.EVENT_READ, None)
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
                    remaining = endtime - monotonic()
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
                    endtime = monotonic() + timeout
                continue
    def _teardown(self):
        self.unregister(self._wake_pipe_read)
        for key in list(self._selector.get_map()):
            _ = self.unregister(key)
        self._selector.close()
        self._selector = None
        os.close(self._wake_pipe_write)
        self._wake_pipe_write = None
        os.close(self._wake_pipe_read)
        self._wake_pipe_read = None

class DriverBase(Dispatcher):

    def __init__(self, config):
        super().__init__()
        self._config = config if config else {}
        self._driver_state = DriverBaseState.CONSTRUCTING
        self._parent = default_driver_parent
        self._name = type(self).__name__
        self._event_thunks = list()
        self._start_before = set()
        self._ok_to_start = True
        self._after_init()
        self._driver_state = DriverBaseState.CONSTRUCTED

    def _after_init(self):
        pass

    @property
    def name(self):
        return self._name

    @property
    def config(self):
        return self._config

    def emits_event(self, event_name):
        assert self._driver_state in CONFIGURATION_STATE
        events = getattr(self, '_EVENTS_', None)
        if events is None:
            return False
        return event_name in events

    def has_values(self):
        assert self._driver_state in CONFIGURATION_STATE
        return False

    def find_driver_by_event(self, event_name, skip_self=True):
        assert self._driver_state in CONFIGURATION_STATE
        skip = self if skip_self else None
        return self._parent.find_driver_by_event(event_name, skip)

    def find_driver_by_name(self, driver_name, skip_self=True):
        assert self._driver_state in CONFIGURATION_STATE
        skip = self if skip_self else None
        return self._parent.find_driver_by_name(driver_name, skip)

    def subscribe(self, driver_name, event_name, id, determines_start_order=True, raise_on_not_found=True, skip_self=True):
        assert self._driver_state in CONFIGURATION_STATE
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
        thunk = DriverThunk(partner, event_name, id, self._event_queue)
        self._event_thunks.append(thunk)
        if (partner != self) and (determines_start_order):
            partner._start_before.add(self)
        return True

    def publish(self, event_name, *args, **kwargs):
        assert self._driver_state in THREAD_ACTIVE_STATE
        return self.emit(event_name, *args, **kwargs)

    #fix
    #def revoke(self):

    def call_after(self, after, method, *args, **kwargs):
        assert self._driver_state in THREAD_ACTIVE_STATE
        event = DriverEvent(method, args, kwargs)
        timelet = DriverTimelet(event, monotonic()+after)
        heapq.heappush(self._timelets, timelet)
        return timelet

    def call_every(self, every, method, *args, **kwargs):
        assert self._driver_state in THREAD_ACTIVE_STATE
        event = DriverEvent(method, args, kwargs)
        fire_now = kwargs.get('fire_now', None)
        if fire_now is not None:
            del kwargs['fire_now']
        else:
            fire_now = False
        timelet = DriverTimeletInterval(event, every, fire_now)
        heapq.heappush(self._timelets, timelet)
        return timelet

    def register(self, fileobj, events, data=None):
        # fix
        assert False
        assert self._driver_state in CONFIGURATION_STATE
        self._event_queue.register(fileobj, events, data)

    def unregister(self, fileobj):
        # fix
        assert False
        self._event_queue.register(fileobj)  # <-- super fix!!!

    def ok_to_start(self):
        assert self._driver_state in CONFIGURATION_STATE
        return self._ok_to_start

    def dont_start(self):
        assert self._driver_state in CONFIGURATION_STATE
        self._ok_to_start = False

    def get(self, block=True, timeout=None):
        # fix: At some point _event_queue.task_done() should be called.
        assert self._driver_state in THREAD_ACTIVE_STATE
        return self._event_queue.get(block=block, timeout=timeout)

    def process_one(self):
        assert self._driver_state in THREAD_ACTIVE_STATE
        while True:
            timeout = None
            while self._timelets:
                delta_to_next_due = self._timelets[0].when_due - monotonic()
                if delta_to_next_due > 0:
                    timeout = delta_to_next_due
                    break
                else:
                    timelet = heapq.heappop(self._timelets)
                    if timelet._enabled:
                        self._event_queue.put(timelet.payload)
                        if timelet.expired():
                            heapq.heappush(self._timelets, timelet)
            try:
                event = self._event_queue.get(block=True, timeout=timeout)
                event.id(*event.args, **event.kwargs)
                return True
            except queue.Empty:
                pass

    def _create_event_queue(self):
        return DriverQueue()

    def start_and_wait(self):
        assert self._driver_state == DriverBaseState.STARTING
        self._open_for_business = Event()
        with self._lock:
            assert self._thread is None
            self._thread = Thread(target=self.run, name=type(self).__name__)
            self._thread.start()
        self._open_for_business.wait()
        self._open_for_business = None

    def join(self):
        with self._lock:
            our_thread = self._thread
        if our_thread:
            our_thread.join()

    def open_for_business(self):
        assert self._driver_state == DriverBaseState.STARTING
        logger.info('{} open for business'.format(self.name))
        self._driver_state = DriverBaseState.STARTED
        self._open_for_business.set()

    def setup(self):
        assert self._driver_state == DriverBaseState.INITIALIZING
        self._lock = Lock()
        self._thread = None
        self._event_queue = self._create_event_queue()
        self._event_queue._setup()
        self._timelets = list()
        self.subscribe(None, DriverSignals.STOP_NOW, self._stop_now, raise_on_not_found=False, skip_self=False)

    def startup(self):
        assert self._driver_state == DriverBaseState.STARTING
        self._keep_running = self._ok_to_start
        self._start_before = None

    def loop(self):
        assert self._driver_state == DriverBaseState.STARTED
        while self._keep_running:
            self.process_one()
        return False

    def _stop_now(self):
        assert self._driver_state == DriverBaseState.STARTED
        self._keep_running = False

    def shutdown(self):
        assert self._driver_state == DriverBaseState.STOPPING
        with self._lock:
            self._thread = None  # rmv? keep? protect?

    def teardown(self):
        assert self._driver_state == DriverBaseState.TEARINGDOWN
        self._event_queue._teardown()
        self._event_queue = None
        self._timelets = None
        # rmv: fix: What can be done with _open_for_business?
        # fix: If revoke is added then reverse the subscribe to STOP_NOW
        self._lock = None
        #self._thread = None  # rmv? keep? protect? assert?

    def run(self):
        assert self._driver_state == DriverBaseState.STARTING
        try:
            self.startup()
            try:
                while self._keep_running:
                    if not self.loop():
                        self._keep_running = False
                self._driver_state = DriverBaseState.STOPPING
            finally:
                self.shutdown()
        except Exception as e:
            # fix? Call a method on self about the exception?
            logging.error("Exception: %s" % str(e), exc_info=1)
            os._exit(42) # Make sure entire application exits

class DeathOfRats(DriverBase):
    _events_ = [DriverSignals.STOP_NOW]
    def startup(self):
        super().startup()
        self.open_for_business()
    def stop_all(self):
        self.publish(DriverSignals.STOP_NOW)
    def shutdown(self):
        super().shutdown()
        self.publish(DriverSignals.STOP_NOW)

