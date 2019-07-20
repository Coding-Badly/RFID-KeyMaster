"""=============================================================================

  Authorizer for RFID-KeyMaster.  Authorizer determines what the human is
  allowed to do from their group membership set.

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
import logging
from rfidkm.drivers.signals import KeyMasterSignals
from rfidkm.drivers.DriverBase import DriverBase
from rfidkm.utils.securitycontext import SecurityContext

logger = logging.getLogger(__name__)

class Authorizer(DriverBase):
    _events_ = [KeyMasterSignals.USER_AUTHORIZED]
    def setup(self):
        super().setup()
        self._context = SecurityContext(
            permissions={
                'power':'User can enable power for the tool.', 
                'unlock':'User can release the latch to gain access.',
                'generic':'Generic permission to ease configuration.'})
        groups = self.config.get('groups', None)
        if groups:
            self._context.add_groups(groups)
        self.subscribe(None, KeyMasterSignals.USER_LOGGED_IN, self.receive_user_logged_in)
    def startup(self):
        super().startup()
        self.open_for_business()
    def receive_user_logged_in(self, data):
        # data is an instance of AuthenticatorData
        effective_rights = self._context.get_effective_rights(data.groups)
        data.effective_rights = effective_rights
        data.authorized = len(effective_rights) > 0
        self.publish(KeyMasterSignals.USER_AUTHORIZED, data)
