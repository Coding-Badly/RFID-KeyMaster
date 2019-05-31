"""=============================================================================

  pytest for PiFaceDigital2Relays.
  
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

from drivers.DriverBase import DriverGroup, DriverBase, DeathOfRats
from drivers.signals import KeyMasterSignals
from drivers.Interface.PiFaceDigital2Interface import PiFaceDigital2Relays
from drivers.Test.RunForSeconds import RunForSeconds
import logging

logger = logging.getLogger(__name__)

class SimpleToggleController(DriverBase):
    _events_ = [KeyMasterSignals.CONTROL_TARGET]
    def startup(self):
        super().startup()
        self._state = 0
        self.call_every(1.95, self.toggle_target, fire_now=True)
        self.open_for_business()
    def toggle_target(self):
        self._state ^= 1
        logger.info('tick {}'.format(self._state))
        self.publish(KeyMasterSignals.CONTROL_TARGET, self._state)

def run_toggle_relay(which, number):
    config = {"driver": "PiFaceDigital2Relays", "init_board": True}
    if "relay" in which:
        config["relay"] = number
    if "group_number" in which:
        config["group_number"] = number
    root = DriverGroup()
    #dor = root.add(DeathOfRats(name='DeathOfRats', config=None, loader=None, id=None))
    dor = root.add(RunForSeconds({'seconds':10.0}))
    pf1 = root.add(PiFaceDigital2Relays(name='Test Me', config=config, loader=None, id=None))
    tm1 = root.add(SimpleToggleController(name='Simple Toggle Controller', config=None, loader=None, id=None))
    root.setup()
    root.start()
    root.join()
    root.teardown()

def run_toggle_relay_N(number):
    run_toggle_relay(frozenset({"relay"}), number)
    run_toggle_relay(frozenset({"group_number"}), number)
    run_toggle_relay(frozenset({"relay", "group_number"}), number)

def test_toggle_relay_0(caplog, exercise_piface_relays):
    if exercise_piface_relays:
        caplog.set_level(logging.INFO)
        run_toggle_relay_N(0)

def test_toggle_relay_1(caplog, exercise_piface_relays):
    if exercise_piface_relays:
        caplog.set_level(logging.INFO)
        run_toggle_relay_N(1)

# rmv def test_toggle_relay_1(caplog):
# rmv     caplog.set_level(logging.INFO)
# rmv     config = {"driver": "PiFaceDigital2Relays", "init_board": True, "relay": 1}
# rmv     run_toggle_relay_N(config)

