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
import logging
import queue
from rfidkm.drivers.DriverBase import DriverBase

logger = logging.getLogger(__name__)

class PingN(DriverBase):
    _events_ = ['receive_ball']
    def setup(self):
        super().setup()
        self._stop_at_1000 = bool(self.config.get('stop_at_1000', True))
        self._last_count = None
    def startup(self):
        super().startup()
        self.open_for_business()

class Ping1(PingN):
    def setup(self):
        super().setup()
        self.subscribe('Pong1', 'receive_ball', 13, determines_start_order=False)
        return True  # rmv
    def startup(self):
        super().startup()
        self.publish('receive_ball', 1)
    def loop(self):
        try:
            event = self.get(timeout=0.100)
            if callable(event.id):
                event.id(*event.args, **event.kwargs)
            else:
                if event.id == 13:
                    count = event.args[0]
                    self._last_count = count
                    if (not self._stop_at_1000) or (count < 1000):
                        self.publish('receive_ball', count+1)
            return True
        except queue.Empty:
            pass
        dor = self.find_driver_by_name('DeathOfRats', True)
        if dor:
            dor.stop_all()
        return False

class Ping2(PingN):
    def setup(self):
        super().setup()
        self.subscribe(None, 'receive_ball', self.receive_ball, determines_start_order=False)
    def startup(self):
        super().startup()
        self.publish('receive_ball', 1)
    def receive_ball(self, count):
        self._last_count = count
        if (not self._stop_at_1000) or (count < 1000):
            self.publish('receive_ball', count+1)
