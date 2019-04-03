"""=============================================================================

  Ping for RFID-KeyMaster testing.  Ping and Pong are meant to test the
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

class Ping(DriverBase):
    _events_ = ['receive_ball']
    def __init__(self):
        super().__init__('Ping', None, None, None)
    def setup(self):
        self.subscribe('Pong', 'receive_ball', 13)
        self._last_count = None
        return True
    def startup(self):
        self.publish('receive_ball', 1)
        pass
    def loop(self):
        try:
            event = self.get(timeout=0.100)
            if event.id == 13:
                count = event.args[0]
                self._last_count = count
                if count < 1000:
                    self.publish('receive_ball', count+1)
            return True
        except queue.Empty:
            pass
        return False
