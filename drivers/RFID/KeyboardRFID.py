"""=============================================================================

  KeyboardRFID for RFID-KeyMaster.  KeyboardRFID is responsible for turning
  RIFD reads from a Sycreader into events.
  
  ----------------------------------------------------------------------------

  Copyright 2019 Mike Cole (aka @Draco, MikeColeGuru)

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
from drivers.RFID.RFID import RFID
from evdev import InputDevice, ecodes
import sys
import logging
import os

class KeyboardRFID(RFID):
    def setup(self):
        self.scancodes = {
            0: None, 2: u'1', 3: u'2', 4: u'3', 5: u'4', 6: u'5', 7: u'6', 8: u'7', 9: u'8', 10: u'9', 11: u'0', 28: u'\n'
        }

        return True

    def loop(self):
        if self.startup:
            # print "scan_daemon: " + str(os.getpid())

            self.dev = InputDevice(self.config['device'])
            self.dev.grab()
            logging.debug(self.dev)
            self.rfid_code = ""

        for event in self.dev.read_loop():
            # If key event and key up (0)
            if event.type == ecodes.EV_KEY and event.value == 0:
                key = self.scancodes.get(event.code)
                if key == u'\n':  # if enter
                    self.emit('swipe', self.rfid_code)
                    logging.debug("RFID scan %s" % self.rfid_code)
                    self.rfid_code = ""
                else:
                    self.rfid_code = self.rfid_code + key


