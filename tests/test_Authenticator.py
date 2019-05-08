"""=============================================================================

  test_Authenticator for RFID-KeyMaster.  test_Authenticator is a pytest
  module for Authenticator.

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
from drivers.DriverBase import DriverGroup, DriverBase
from drivers.Test.RunForSeconds import RunForSeconds
import logging
from time import monotonic

logger = logging.getLogger(__name__)

class MemberDataAndSwipe10Stub(DriverBase):
    _events_ = [Signals.CACHED_DATA, Signals.FRESH_DATA, Signals.SWIPE_10]
    def setup(self):
        super().setup()
        self.subscribe(None, Signals.USER_LOGGED_IN, self.receive_user_logged_in, determines_start_order=False)
        self.subscribe(None, Signals.USER_LOGIN_FAILED, self.receive_user_login_failed, determines_start_order=False)
    def startup(self):
        super().startup()
        self.open_for_business()
        member_data = {
            '0002864796':{  # blue tag
                'user':{
                    'fullName':'Bugs Bunny', 
                    'groups':['Loves Carrots', 'Torments Elmer Fudd'], 
                    'username':'bugs'}},
            '0006276739':{  # red tag
                'user':{
                    'fullName':'Elmer Fudd',
                    'groups':['Carries Shotgun', 'Hunts Wabbit'],
                    'username':'fudd'}}}
        self.publish(Signals.CACHED_DATA, member_data)
        self.call_after(0.10, self.publish_first_swipe10)
    def publish_first_swipe10(self):
        logger.info('SWIPE!')
        self.publish(Signals.SWIPE_10, monotonic(), '0002864796')  # blue tag
    def receive_user_logged_in(self, authenticator_data):
        logger.info('OK:   %s', authenticator_data)
        if authenticator_data.rfid == '0002864796':  # blue tag
            self.publish(Signals.SWIPE_10, monotonic(), '0000721130')  # Brian's tag
        elif authenticator_data.rfid == '0006276739':  # red tag
            self.publish(Signals.SWIPE_10, monotonic(), '0008683072')  # purple tag
        elif authenticator_data.rfid == '0008683072':  # purple tag
            self.publish(Signals.CACHED_DATA, {})
            self.publish(Signals.SWIPE_10, monotonic(), '0004134263')  # black tag
        elif authenticator_data.rfid == '0004134263':  # black tag
            self.fini = True
    def receive_user_login_failed(self, authenticator_data):
        logger.info('FAIL: %s', authenticator_data)
        if authenticator_data.rfid == '0000721130':  # Brian's tag
            self.publish(Signals.SWIPE_10, monotonic(), '0006276739')  # red tag
        elif authenticator_data.rfid == '0008683072':  # purple tag
            self.publish(Signals.FRESH_DATA, {})
            self.publish(Signals.SWIPE_10, monotonic(), '0002864796')  # blue tag
        elif authenticator_data.rfid == '0002864796':  # blue tag
            self.publish(Signals.SWIPE_10, monotonic(), '0006276739')  # red tag
        elif authenticator_data.rfid == '0006276739':  # red tag
            member_data = {
                '0008683072':{  # purple tag
                    'user':{
                        'fullName':'Foghorn Leghorn', 
                        'groups':['Pranks Barnyard Dawg'], 
                        'username':'senator_claghorn'}},
                '0004134263':{  # black tag
                    'user':{
                        'fullName':'Porky Pig',
                        'groups':["That's all Folks!"],
                        'username':'El_Puerco'}}}
            self.publish(Signals.FRESH_DATA, member_data)
            self.publish(Signals.SWIPE_10, monotonic(), '0008683072')  # purple tag

def test_Authenticator(caplog):
    caplog.set_level(logging.INFO)
    root = DriverGroup('root')
    aut = root.add(Authenticator('Default Authenticator', None, None, None))
    stu = root.add(MemberDataAndSwipe10Stub('Stub', None, None, None))
    dor = root.add(RunForSeconds(1.0))
    root.setup()
    root.start()
    root.join()
    root.teardown()
    assert stu.fini

