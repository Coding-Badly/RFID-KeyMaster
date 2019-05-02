"""=============================================================================

  pytest for SycreaderUSB125.

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
import platform
import pytest

if platform.system() == 'Windows':
    pytest.skip("skipping tests that will not run on Windows", allow_module_level=True)

from drivers import Signals
from drivers.DriverBase import DriverBase
import logging

logger = logging.getLogger(__name__)

class SimplePrintTagController(DriverBase):
    def setup(self):
        super().setup()
        self.subscribe(None, Signals.SWIPE_10, self.receive_swipe_10)
    # self.publish(Signals.SWIPE_10, self._parser.timestamp, self._parser.rfid)
    def receive_swipe_10(self, timestamp, rfid):
        logger.info('rfid {} {}'.format(timestamp, rfid))

def run_rfid_reader(config):
    root = DriverGroup()
    dor = root.add(RunForSeconds(10.0))
    jk1 = root.add(SycreaderUSB125(name='Test Me', config=config, loader=None, id=None))
    tm1 = root.add(SimplePrintTagController(name='Simple Print Tag Controller', config=None, loader=None, id=None))
    root.setup()
    root.start()
    root.join()
    root.teardown()

def test_reader_0(caplog):
    caplog.set_level(logging.INFO)
    config = {"driver": "SycreaderUSB125", "reader": 0}
    run_rfid_reader(config)

