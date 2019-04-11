"""=============================================================================

  Driver for the Sycreader 125 kHz RFID tag reader.  The device normally
  behaves like a keyboard but for this application it is treated as a raw USB
  device.  This code will only work on Linux.  A "swipe10" event is published
  on a successful read.

  ----------------------------------------------------------------------------

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
from drivers.DriverBase import DriverQueuePlusSelect, DriverBase, DriverGroup, DeathOfRats
from enum import Enum
import evdev
import selectors

def find_el_cheapo_rfid_reader():
    return [device for device in [evdev.InputDevice(path) for path in evdev.list_devices()] if 'SYCREADER' in device.name.upper()]

class ParserStatus(Enum):
    UNKNOWN = 0
    PENDING = 1
    RESET = 2
    FINI = 3
    ERROR = 4

class SycreaderParser():
    def __init__(self):
        self._rfid = ''
        self._timestamp = None
        self._reset()
    def _process_digit(self, wrapped):
        # KEY_0 through KEY_9
        kc = wrapped.keycode
        if len(kc) == 5:
            digit = kc[-1]
            if (digit >= '0') and (digit <= '9'):
                self._pending += digit
                return True
            return False
    def _reset(self):
        self._state = self.wait_for_first_event
        self._start = None
        self._stop = None
        self._pending = ''
    def wait_for_first_event(self, wrapped):
        if self._process_digit(wrapped):
            self._state = self.collecting
            self._start = wrapped.event.timestamp()
            self._stop = self._start
            return ParserStatus.PENDING
        else:
            # Unexpected keycode
            self._reset()
            return ParserStatus.ERROR
    def collecting(self, wrapped):
        self._stop = wrapped.event.timestamp()
        elapsed = self._stop - self._start
        if elapsed > 0.250:
            self._reset()
            # fix? Report the trouble?
            return ParserStatus.RESET
        if self._process_digit(wrapped):
            return ParserStatus.PENDING
        elif wrapped.keycode == 'KEY_ENTER':
            self._rfid = self._pending
            self._timestamp = self._stop
            self._reset()
            return ParserStatus.FINI
        else:
            # Unexpected keycode
            self._reset()
            # fix? Report the error?
            return ParserStatus.ERROR
    def process(self, wrapped):
        rv2 = ParserStatus.UNKNOWN
        rv1 = self._state(wrapped)
        if rv1 == ParserStatus.RESET:
            rv2 = self._state(wrapped)
        if rv1.value > rv2.value:
            return rv1
        else:
            return rv2
    @property
    def rfid(self):
        # fix? Report trouble / raise an exception if ParserStatus.FINI was not reached?
        return self._rfid
    @property
    def timestamp(self):
        return self._timestamp

class SycreaderUSB125(DriverBase):
    _events_ = ['swipe10']
    def _create_event_queue(self):
        return DriverQueuePlusSelect()
    def setup(self):
        super().setup()
        # fix: Fail if the number of readers found is not one?
        self._device = find_el_cheapo_rfid_reader()[0]
        self._parser = SycreaderParser()
        self.register(self._device, selectors.EVENT_READ, self.process)
    def process(self, selector_key, mask):
        event = selector_key.fileobj.read_one()
        if event.type == evdev.ecodes.EV_KEY:
            cooked = evdev.util.categorize(event)
            if cooked.keystate == cooked.key_up:
                rv = self._parser.process(cooked)
                if rv == ParserStatus.FINI:
                    self.publish('swipe10', self._parser.timestamp, self._parser.rfid)
                    # rmv print(self._parser.timestamp, self._parser.rfid)
                    # rmv self.target.got_swipe(self.parser)
                # ParserStatus.ERROR
        # rmv print(evdev.categorize(event), mask)
    def teardown(self):
        super().teardown()
        self._device = None
        self._parser = None

