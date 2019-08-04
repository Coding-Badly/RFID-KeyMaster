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
import logging
from rfidkm.drivers.signals import KeyMasterSignals
from rfidkm.drivers.DriverBase import DriverBase

logger = logging.getLogger(__name__)

# user_logged_in
#   user
# user_logged_out
#   user
# user_login_failed
#   credentials

class AuthenticatorData():
    def __init__(self, rfid):
        self._rfid = rfid
        self._username = None
        self._human_name = None
        self._groups = []
    def __str__(self):
        t1 = self._human_name if self._human_name else 'n/a'
        t2 = ' (' + self._username + ')' if self._username else ''
        return '{!s}: {!s}{!s} {!s}'.format(self._rfid, t1, t2, self._groups)
    def from_member_data(self, member_data):
        user_data = member_data['user']
        self._username = user_data['username']
        self._human_name = user_data['fullName']
        self._groups = frozenset(user_data['groups'])
    @property
    def rfid(self):
        return self._rfid
    @property
    def username(self):
        return self._username
    @property
    def human_name(self):
        return self._human_name
    @property
    def groups(self):
        return self._groups

class Authenticator(DriverBase):
    _events_ = [KeyMasterSignals.USER_LOGGED_IN, KeyMasterSignals.USER_LOGIN_FAILED]
    def setup(self):
        super().setup()
        self._have_fresh_data = False
        self._member_data = dict()
        self.subscribe(None, KeyMasterSignals.CACHED_DATA, self.receive_cached_data)
        self.subscribe(None, KeyMasterSignals.FRESH_DATA, self.receive_fresh_data)
        self.subscribe(None, KeyMasterSignals.SWIPE_10, self.receive_swipe_10)
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
        t1 = AuthenticatorData(rfid)
        if member_data:
            logger.info('"{}" authenticated; publishing a USER_LOGGED_IN.'.format(rfid))
            t1.from_member_data(member_data)
            self.publish(KeyMasterSignals.USER_LOGGED_IN, t1)
        else:
            logger.info('"{}" failed to authenticate; publishing a USER_LOGIN_FAILED.'.format(rfid))
            # fix? Should MemberDataFreshener check for fresh data when a login failure occurs?
            self.publish(KeyMasterSignals.USER_LOGIN_FAILED, t1)
