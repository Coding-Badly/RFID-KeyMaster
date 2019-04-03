"""=============================================================================

  DriverBase for RFID-KeyMaster.  DriverBase is a base class for all run-time
  loadable drivers.  Each DriverBase is also a Thread allowing it to block
  without interfering with other parts of the application.  DriverBase provides
  three services: 1. Connection to configuration data and a parent; 2. Find
  siblings so drivers can interact directly with each other; 3. Turn all
  unexpected exceptions into a clean exit.
  
  ----------------------------------------------------------------------------

  Copyright 2019 Mike Cole (aka @Draco, MikeColeGuru)
  Copyright 2019 Brian Cook (aka Coding-Badly)

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
import logging
import os
from pydispatch import Dispatcher
import queue
import heapq

next_name_index = 1

def get_next_name():
    global next_name_index
    rv = 'whatever #{}'.format(next_name_index)
    next_name_index += 1
    return rv

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
        assert driver_or_group._parent is None
        self[driver_or_group.name] = driver_or_group
        driver_or_group._parent = self
        return driver_or_group

    def find_driver_by_event(self, event_name):
        return self._find_driver_by_event_in_children(event_name, None)

    def _find_driver_by_event_in_children(self, event_name, skip):
        if skip == self:
            return None
        for driver_or_group in self.values():
            rv = driver_or_group._find_driver_by_event_in_children(event_name, skip)
            if rv is not None:
                break
        if rv is None:
            if self._parent is not None:
                return self._parent._find_driver_by_event_in_children(event_name, self)
        return rv

    def find_driver_by_name(self, driver_name):
        return self._find_driver_by_name_in_children(driver_name, None)

    def _find_driver_by_name_in_children(self, driver_name, skip):
        # Short-circuit.  Most queries should stop here.
        rv = self.get(driver_name, None)
        if rv is not None:
            return rv
        # Breadth-first search down then working up.
        heap = list()
        anchor = self
        order = 1
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
                    # fix? Use a method call instead of isinstance?  child.has_values for example?
                    if (child != skip) and isinstance(child, DriverGroup):
                        heapq.heappush(heap, (priority, order, child))
                        order += 1
            skip = anchor
            anchor = anchor._parent
        if driver_name == self.name:
            return self
        return None

    def setup(self):
        # fix? Do something with the return values?
        # fix? Fail to run if any return False?
        self._startable.clear()
        for driver_or_group in self.values():
            if driver_or_group.setup():
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

class DriverBase(Thread, Dispatcher):
    def __init__(self, name, config, loader, id):
        self._parent = None
        self._name = name
        self.config = config
        self.loader = loader
        self.id = id
        self._event_queue = queue.Queue()
        self._event_thunks = list()
        super().__init__(name=name)

    @property
    def name(self):
        return self._name

    def setup(self):
        return False

    def startup(self):
        pass

    def loop(self):
        return False

    def shutdown(self):
        pass

    def teardown(self):
        # fix: Teardown is currently not used.  This method is the inverse of
        # setup.  Whatever is down in setup should be undone in teardown.  If
        # this method is ever brought into play it will be called in the same
        # basic fashion as setup.
        pass

    def find_driver_by_event(self, event_name):
        return self._parent._find_driver_by_event_in_children(event_name, self)

    def _find_driver_by_event_in_children(self, event_name, skip):
        if skip == self:
            return None
        events = getattr(self, '_events_', None)
        if events is None:
            return None
        if event_name in events:
            return self
        return None

    def find_driver_by_name(self, driver_name):
        return self._parent._find_driver_by_name_in_children(driver_name, self)

    def getDriver(self, driver_name, controller=None):
        driver = self.loader.getDriver(driver_name, controller)
        if driver == None:
            raise RequiredDriverException(driver_name)
        return driver  

    def subscribe(self, driver_name, event_name, id):
        if driver_name is None:
            pass
        else:
            partner = self.find_driver_by_name(driver_name)
            if partner is None:
                raise RequiredDriverException(driver_name)
            thunk = DriverThunk(partner, event_name, id, self._event_queue)
            self._event_thunks.append(thunk)

    def publish(self, event_name, *args, **kwargs):
        self.emit(event_name, args, kwargs)
    
    #fix
    #def revoke(self):

    def get(self, block=True, timeout=None):
        return self._event_queue.get(block=block, timeout=timeout)

    def run(self):
        try:
            self.startup()
            # rmv self.startup = True
            try:
                while self.loop() != False:
                    pass
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

