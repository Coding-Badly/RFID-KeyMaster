"""=============================================================================

  Pong for RFID-KeyMaster testing.  Ping and Pong are meant to test the
  threading and messaging of RFID-KeyMaster.  The two simply pass an event back
  and forth.
  
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
from drivers.DriverBase import DriverBase
import queue

class RunForSeconds(DriverBase):
    _events_ = [DriverBase.EVENT_STOP_NOW]
    def __init__(self, seconds):
        super().__init__('RunForSeconds', None, None, None)
        self._seconds = seconds
    def loop(self):
        try:
            event = self.get(timeout=self._seconds)
        except queue.Empty:
            pass
        return False
    def shutdown(self):
        super().shutdown()
        self.publish(DriverBase.EVENT_STOP_NOW)
