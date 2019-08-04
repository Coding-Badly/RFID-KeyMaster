"""=============================================================================

  SimpleToggleController for RFID-KeyMaster.  This controller toggles a PiFace
  Digital 2 relay about every two seconds.

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
import logging

from rfidkm.drivers.DriverBase import DriverBase
from rfidkm.drivers.signals import KeyMasterSignals

logger = logging.getLogger(__name__)

class SimpleToggleController(DriverBase):
    _events_ = [KeyMasterSignals.CONTROL_RELAY]
    def setup(self):
        super().setup()
        self._toggle_rate = float(self.config.get('toggle_rate', 1.95))
    def startup(self):
        super().startup()
        self._state = 0
        self.call_every(self._toggle_rate, self.toggle_relay, fire_now=True)
        self.open_for_business()
    def toggle_relay(self):
        self._state ^= 1
        logger.info('tick {}'.format(self._state))
        self.publish(KeyMasterSignals.CONTROL_RELAY, self._state)

