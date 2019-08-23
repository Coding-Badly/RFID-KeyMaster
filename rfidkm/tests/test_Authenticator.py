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
import logging
from time import monotonic

from rfidkm.drivers.signals import KeyMasterSignals
from rfidkm.drivers.Auth.Authenticator import Authenticator
from rfidkm.drivers.DriverBase import DriverGroup, DriverBase
from rfidkm.drivers.Test.RunForSeconds import RunForSeconds

logger = logging.getLogger(__name__)

class MemberDataAndSwipe10Stub(DriverBase):
    _events_ = [KeyMasterSignals.CACHED_DATA, KeyMasterSignals.FRESH_DATA, KeyMasterSignals.SWIPE_10]
    def setup(self):
        super().setup()
        self._death_of_rats = self.config.get('DeathOfRats', None)
        self.subscribe(None, KeyMasterSignals.USER_LOGGED_IN, self.receive_user_logged_in, determines_start_order=False)
        self.subscribe(None, KeyMasterSignals.USER_LOGIN_FAILED, self.receive_user_login_failed, determines_start_order=False)
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
        self.publish(KeyMasterSignals.CACHED_DATA, member_data)
        self.call_after(0.10, self.publish_first_swipe10)
    def publish_first_swipe10(self):
        logger.info('SWIPE!')
        self.publish(KeyMasterSignals.SWIPE_10, monotonic(), '0002864796')  # blue tag
    def receive_user_logged_in(self, authenticator_data):
        logger.info('OK:   %s', authenticator_data)
        if authenticator_data.rfid == '0002864796':  # blue tag
            self.publish(KeyMasterSignals.SWIPE_10, monotonic(), '0000721130')  # Brian's tag
        elif authenticator_data.rfid == '0006276739':  # red tag
            self.publish(KeyMasterSignals.SWIPE_10, monotonic(), '0008683072')  # purple tag
        elif authenticator_data.rfid == '0008683072':  # purple tag
            self.publish(KeyMasterSignals.CACHED_DATA, {})
            self.publish(KeyMasterSignals.SWIPE_10, monotonic(), '0004134263')  # black tag
        elif authenticator_data.rfid == '0004134263':  # black tag
            self.fini = True
            if self._death_of_rats:
                self._death_of_rats.stop_all()
    def receive_user_login_failed(self, authenticator_data):
        logger.info('FAIL: %s', authenticator_data)
        if authenticator_data.rfid == '0000721130':  # Brian's tag
            self.publish(KeyMasterSignals.SWIPE_10, monotonic(), '0006276739')  # red tag
        elif authenticator_data.rfid == '0008683072':  # purple tag
            self.publish(KeyMasterSignals.FRESH_DATA, {})
            self.publish(KeyMasterSignals.SWIPE_10, monotonic(), '0002864796')  # blue tag
        elif authenticator_data.rfid == '0002864796':  # blue tag
            self.publish(KeyMasterSignals.SWIPE_10, monotonic(), '0006276739')  # red tag
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
            self.publish(KeyMasterSignals.FRESH_DATA, member_data)
            self.publish(KeyMasterSignals.SWIPE_10, monotonic(), '0008683072')  # purple tag

def test_Authenticator(caplog):
    caplog.set_level(logging.INFO)
    root = DriverGroup('root')
    dor = root.add(RunForSeconds(config={'seconds':1.0}))
    aut = root.add(Authenticator(config=None))
    stu = root.add(MemberDataAndSwipe10Stub(config={'DeathOfRats':dor, 'name':'Stub'}))
    root.setup()
    root.start()
    root.join()
    root.teardown()
    assert stu.fini

