"""=============================================================================

  Authenticator for RFID-KeyMaster.  Authenticator turns swipe_10 events into
  member_login events.

  ----------------------------------------------------------------------------

  Copyright 2019 Mike Cole (aka @Draco, MikeColeGuru)
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

class Authenticator(DriverBase):
    _events_ = [Signals.LOGIN_RFID_NOT_FOUND, Signals.LOGIN_PERMISSION_DENIED, Signals.LOGIN_SUCCESS]
    def setup(self):
        super().setup()
        self._have_fresh_data = False
        self._member_data = dict()
        self.subscribe(None, Signals.CACHED_DATA, self.receive_cached_data)
        self.subscribe(None, Signals.FRESH_DATA, self.receive_fresh_data)
        self.subscribe(None, Signals.SWIPE_10, self.receive_swipe_10)
    def startup(self):
        super().startup()
        self.open_for_business()
    def receive_cached_data(self, data):
        if not self._have_fresh_data:
            self._member_data = data
    def receive_fresh_data(self, data):
        self._member_data = data
        self._have_fresh_data = True
    def receive_swipe_10(self, timestamp, rfid):
        member_data = self._member_data.get(rfid, None)
        if member_data:
            pass
        else:
            self.publish(Signals.LOGIN_RFID_NOT_FOUND, rfid)
