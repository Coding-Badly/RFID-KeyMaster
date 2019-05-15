"""=============================================================================

  RunForSeconds for RFID-KeyMaster testing.  RunForSeconds is a driver that
  runs for a specified number of seconds then requests all other Drivers 
  terminate.

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
from drivers.DriverBase import DriverBase, DeathOfRats
# import logging

# logger = logging.getLogger(__name__)

class RunForSeconds(DeathOfRats):
    def setup(self):
        super().setup()
        self._seconds = float(self.config.get('seconds', 1.0))
    def startup(self):
        super().startup()
        self.call_after(self._seconds, self._stop_now)
