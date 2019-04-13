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
import queue

class RunForSeconds(DeathOfRats):
    def __init__(self, seconds):
        super().__init__('RunForSeconds', None, None, None)
        self._seconds = seconds
    def loop(self):
        self.process_one(timeout=self._seconds)
        while self.process_one(timeout=0):
            pass
        return False

