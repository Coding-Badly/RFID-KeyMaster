"""=============================================================================

  test_Authorizer for RFID-KeyMaster.  test_Authorizer is a pytest module for 
  Authorizer.

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
from drivers.Auth.Authenticator import Authenticator
from drivers.Auth.Authorizer import Authorizer
from drivers.Auth.Authenticator import AuthenticatorData
from drivers.DriverBase import DriverGroup, DriverBase
from drivers.Test.RunForSeconds import RunForSeconds
from utils.SecurityContext import Permission
import json
import logging
from time import monotonic

logger = logging.getLogger(__name__)

class MemberLoginStub(DriverBase):
    _events_ = [Signals.CACHED_DATA, Signals.FRESH_DATA, Signals.SWIPE_10]
    def setup(self):
        super().setup()
        self._death_of_rats = self.config.get('DeathOfRats', None)
        self._state = 1
        self._red = 0
        self._blue = 0
        self.subscribe(None, Signals.USER_AUTHORIZED, self.receive_user_authorized, determines_start_order=False)
        self.subscribe(None, Signals.USER_LOGIN_FAILED, self.receive_user_login_failed, determines_start_order=False)
    def startup(self):
        super().startup()
        self.open_for_business()
        self.call_after(0.10, self.publish_first_swipe10)
    def publish_first_swipe10(self):
        self.publish(Signals.SWIPE_10, monotonic(), '0006276739')  # red tag
    def receive_user_authorized(self, data):
        if data.rfid == '0006276739':  # red tag
            assert self._state == 2
            self._red += 1
            assert data.authorized
            assert Permission('power') in data.effective_rights
            if self._red == 1:
                self.publish(Signals.SWIPE_10, monotonic(), '0006276739')  # red tag
            else:
                self.publish(Signals.SWIPE_10, monotonic(), '0002864796')  # blue tag
        elif data.rfid == '0002864796':  # blue tag
            assert self._state == 2
            self._blue +=1
            assert not data.authorized
            assert not (Permission('power') in data.effective_rights)
            if self._death_of_rats:
                self._death_of_rats.stop_all()
    def receive_user_login_failed(self, data):
        if data.rfid == '0006276739':  # red tag
            assert self._state == 1
            self.publish(Signals.SWIPE_10, monotonic(), '0002864796')  # blue tag
        elif data.rfid == '0002864796':  # blue tag
            assert self._state == 1
            self._state += 1
            member_data = {
                '0002864796':{  # blue tag
                    'user':{
                        'fullName':'Blue Jay', 
                        'groups':['Members'], 
                        'username':'bluejay'}},
                '0006276739':{  # red tag
                    'user':{
                        'fullName':'Red Green',
                        'groups':['Members', 'Automotive 102 (Lift Training)'],
                        'username':'redgreen'}}}
            self.publish(Signals.CACHED_DATA, member_data)
            self.publish(Signals.SWIPE_10, monotonic(), '0006276739')  # red tag

def test_authenticator_001(caplog):
    #caplog.set_level(logging.INFO)
    raw = '{"groups": [["Automotive 102 (Lift Training)", "power"]]}'
    py1 = json.loads(raw)
    root = DriverGroup('root')
    dor = root.add(RunForSeconds(1.00))
    aut = root.add(Authenticator('Default Authenticator', None, None, None))
    aut = root.add(Authorizer('Default Authorizer', py1, None, None))
    stu = root.add(MemberLoginStub('Stub', {'DeathOfRats':dor}, None, None))
    root.setup()
    root.start()
    root.join()
    root.teardown()

