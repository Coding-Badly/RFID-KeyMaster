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
import logging
import queue

class Pong1(DriverBase):
    _events_ = ['receive_ball']
    def __init__(self):
        super().__init__('Pong1', None, None, None)
    def setup(self):
        super().setup()
        self.subscribe(None, 'receive_ball', self.receive_ball)
        self._last_count = None
        return True  # rmv
    def loop(self):
        try:
            event = self.get(timeout=0.100)
            event.id(*event.args, **event.kwargs)
            return True
        except queue.Empty:
            pass
        return False
    def receive_ball(self, count):
        self._last_count = count
        self.publish('receive_ball', count+1)
