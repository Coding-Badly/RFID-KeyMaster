"""=============================================================================

  AutomaticLogout for RFID-KeyMaster.  AutomaticLogout automatically logs-out
  the current user when a set of specified conditions are met.  The conditions
  for power are: no current flow detected in the previous five minutes and the
  same person has been logged-in for those five minutes.

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
from rfidkm.drivers.signals import KeyMasterSignals
from rfidkm.drivers.DriverBase import DriverBase

class AutomaticLogout(DriverBase):
    def setup(self):
        super().setup()
        self.subscribe(None, KeyMasterSignals.USER_LOGGED_IN, self.receive_user_logged_in)
        self.subscribe(None, KeyMasterSignals.USER_LOGIN_FAILED, self.receive_user_login_failed)
        self.subscribe(None, KeyMasterSignals.USER_AUTHORIZED, self.receive_user_authorized)
    def startup(self):
        super().startup()
        self.open_for_business()
    def receive_user_logged_in(self, data):
        # Note: data is an AuthenticatorData instance.
        pass
    def receive_user_login_failed(self, data):
        # Note: data is an AuthenticatorData instance.
        pass
    def receive_user_authorized(self, data):
        # Note: data is an AuthenticatorData instance with effective_rights and authorized added
        pass

