"""=============================================================================

  PowerController for RFID-KeyMaster.  PowerController creates a gadget that
  controls power.  If a member is authorized to power the tool then this
  controller turns on a digital output (typically connected to a relay).  If a
  member is not authorized then this controller turns off that digital output.

  ----------------------------------------------------------------------------

  Copyright 2019 Mike Cole (aka @Draco, MikeColeGuru)

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
from utils.SecurityContext import Permission
import logging

logger = logging.getLogger(__name__)

class PowerController(DriverBase):
    _events_ = [Signals.CONTROL_TARGET]
    def setup(self):
        super().setup()
        self._power_permission = Permission('power')
        self._current_user = None
        self._target_state = None
        self.subscribe(None, Signals.USER_AUTHORIZED, self.receive_user_authorized)
        self.subscribe(None, Signals.USER_LOGIN_FAILED, self.receive_user_login_failed)
    def startup(self):
        super().startup()
        self.open_for_business()
    def _control_target(self, new_state):
        new_value = 1 if new_state else 0
        self.publish(Signals.CONTROL_TARGET, new_value)
        self._target_state = new_state
    def receive_user_authorized(self, data):
        if data.authorized and (self._power_permission in data.effective_rights):
            # Log an info
            self._current_user = data
            # Power on!
            self._control_target(True)
        else:
            # Log a warning.
            self._current_user = None
            self._control_target(False)
    def receive_user_login_failed(self, data):
        # Power off!
        # Issue a warning.
        # Don't power off if current is flowing?
        # Issue a warning if current is flowing?
        self._current_user = None
        self._control_target(False)

