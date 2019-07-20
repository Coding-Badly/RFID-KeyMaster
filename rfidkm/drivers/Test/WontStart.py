"""=============================================================================

  WontStart for RFID-KeyMaster.  WontStart is a driver that ... 
  you guessed it ... won't start.  It's purpose is to test a failure during
  setup.

  ----------------------------------------------------------------------------

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
import logging
from rfidkm.drivers.DriverBase import DriverBase

logger = logging.getLogger(__name__)

class WontStart(DriverBase):
    def setup(self):
        super().setup()
        logger.error('Refusing to start for no particular reason.')
        self.dont_start()
    def startup(self):
        super().startup()
        self.open_for_business()

