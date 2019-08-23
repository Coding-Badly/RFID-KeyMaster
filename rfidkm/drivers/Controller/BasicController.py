"""=============================================================================

  BasicController for RFID-KeyMaster.  BasicController creates a gadget that
  controls power.  If a member is authorized to power the tool then this
  controller turns on a digital output (typically connected to a relay).  If a
  member is not authorized then this controller turns off that digital output.

  ----------------------------------------------------------------------------

  Copyright 2019 Brian Cook (aka @Brian, Coding-Badly)
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
import logging
from rfidkm.drivers.signals import KeyMasterSignals, UserAuthorizedEvent, UserDeniedEvent
from rfidkm.drivers.DriverBase import DriverBase
from rfidkm.locktypes import create_state_machine
from rfidkm.utils.securitycontext import Permission

logger = logging.getLogger(__name__)

class BasicController(DriverBase):
    _events_ = [KeyMasterSignals.CONTROL_RELAY]
    def setup(self):
        super().setup()
        self._power_permission = Permission('power')
        lock_type = self.config.get('lock_type', 'BasicPowerControl')
        class_name = lock_type + 'StateMachine'
        self._state_machine = create_state_machine(class_name, self, self.config)
        self.subscribe(None, KeyMasterSignals.USER_AUTHORIZED, self._receive_user_authorized)
        self.subscribe(None, KeyMasterSignals.USER_LOGIN_FAILED, self._receive_user_login_failed)
        self.subscribe(None, KeyMasterSignals.CURRENT_FLOWING, self._receive_current_flowing)
        self.subscribe(None, KeyMasterSignals.RELAY_CLOSED, self._receive_relay_closed, determines_start_order=False)
    def startup(self):
        super().startup()
        self.open_for_business()
    def _receive_user_authorized(self, data):
        logger.info('receive_user_authorized...')
        logger.info('{}'.format(data.rfid))
        logger.info('{}'.format(data.authorized))
        self._state_machine.process(UserAuthorizedEvent(data.rfid))
    def _receive_user_login_failed(self, data):
        logger.info('receive_user_login_failed...')
        logger.info('{}'.format(data.rfid))
        self._state_machine.process(UserDeniedEvent(data.rfid))
    def _receive_current_flowing(self, value):
        logger.info('receive_current_flowing...')
        logger.info('{}'.format(value))
        self._state_machine.process_current_flowing(value)
    def _receive_relay_closed(self, value):
        logger.info('receive_relay_closed...')
        logger.info('{}'.format(value))
        self._state_machine.process_relay_closed(value)
    def close_relay(self):
        # fix? rmv? self._state_machine.relay_is_closed = True
        # fix? rmv? 
        log_during_test(self._subject, 'close the relay')
        self.publish(KeyMasterSignals.CONTROL_RELAY, True)
    def open_relay(self):
        # fix? rmv? self._state_machine.relay_is_closed = False
        # fix? rmv? 
        log_during_test(self._subject, 'open the relay')
        self.publish(KeyMasterSignals.CONTROL_RELAY, False)
    def start_timeout_timer(self, seconds):
        # fix? rmv? log_during_test(self._subject, 'post a timeout in {} seconds'.format(seconds))
    def stop_timeout_timer(self):
        # fix? rmv? log_during_test(self._subject, 'cancel the timeout request')
    def log(lvl, msg, *args, **kwargs):
        pass
