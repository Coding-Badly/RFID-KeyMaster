"""=============================================================================

  HardwareStartupCheck.py for RFID-KeyMaster.  HardwareStartupCheck is
  essentially a Controller.  It's purpose is to capture the startup state of
  the hardware (relay state, current flowing sensor).  The goal is to ensure
  the hardware is correctly initialized and the appropriate drivers are
  correctly reporting the startup state.  At the time this was written a human
  has to participate (actually manipulate the relay with another program /
  trigger the current sensor).

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
from drivers import Signals
from drivers.DriverBase import DriverBase
import logging

logger = logging.getLogger(__name__)

class HardwareStartupCheck(DriverBase):
    _events_ = [Signals.CONTROL_TARGET]
    def _after_init(self):
        super()._after_init()
        self.current_was_flowing = None
        self.target_was_engaged = None
    def setup(self):
        super().setup()
        self.expected_current_was_flowing = self.config.get('expected_current_was_flowing', None)
        self.expected_target_was_engaged = self.config.get('expected_target_was_engaged', None)
        self.subscribe(None, Signals.CURRENT_FLOWING, self._receive_current_flowing)
        self.subscribe(None, Signals.TARGET_ENGAGED, self._receive_target_engaged, determines_start_order=False)
    def startup(self):
        super().startup()
        self.call_after(0.10, self._finished)
        self.open_for_business()
    def _receive_current_flowing(self, *args, **kwargs):
        current_flowing = args[0]
        if self.current_was_flowing is None:
            self.current_was_flowing = current_flowing
        logger.info('receive_current_flowing / current_flowing = {}'.format(current_flowing))
    def _receive_target_engaged(self, target_engaged):
        if self.target_was_engaged is None:
            self.target_was_engaged = target_engaged
        logger.info('receive_target_engaged / target_engaged = {}'.format(target_engaged))
    def _finished(self):
        dor = self.find_driver_by_name('DeathOfRats', True)
        if dor:
            dor.stop_all()
    def teardown(self):
        if self.expected_current_was_flowing is not None:
            assert self.expected_current_was_flowing == self.current_was_flowing
        if self.expected_target_was_engaged is not None:
            assert self.expected_target_was_engaged == self.target_was_engaged
