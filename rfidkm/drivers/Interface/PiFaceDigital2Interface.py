"""=============================================================================

  PiFaceDigital2Interface for RFID-KeyMaster.

  PiFaceDigital2Relays is a driver for the relays on the PiFace Digital 2 HAT.

  PiFaceDigital2SimulateCurrentSensor toggles the current flow state when a
  pushbutton is pressed on the HAT.

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
import pifacedigitalio
# rmv import atexit
from rfidkm.drivers.signals import KeyMasterSignals
from rfidkm.drivers.DriverBase import DriverBase

logger = logging.getLogger(__name__)

# The following is required for the board to function correctly.  It only
# needs to be done once after power-up.  At the time this comment was written
# it has been moved to a service (init_PiFace_Digital_2.service) that runs once
# on each power-up.

#pifacedigitalio.core.init()

class PiFaceDigital2Relays(DriverBase):
    _events_ = [KeyMasterSignals.RELAY_CLOSED]
    def setup(self):
        super().setup()
        group_number = int(self.config.get('group_number', 0))
        init_board = self.config.get('init_board', False)
        self._relay = int(self.config.get('relay', group_number))
        # Turn off Interrupts
        # rmv? pifacedigitalio.core.deinit()
        self._pifacedigital = pifacedigitalio.PiFaceDigital(init_board=init_board)
        self.subscribe(None, KeyMasterSignals.CONTROL_RELAY, self._receive_control_relay)
        # rmv atexit.register(self.reset_piface)
        #return False
    def _publish_relay_state(self):
        self.publish(KeyMasterSignals.RELAY_CLOSED, bool(self._pifacedigital.relays[self._relay].value))
    def startup(self):
        super().startup()
        self._publish_relay_state()
        self.open_for_business()
    def _receive_control_relay(self, data):
        new_value = int(data)
        self._pifacedigital.relays[self._relay].value = new_value
        self._publish_relay_state()
        logger.info('relay set to = {}'.format(new_value))
    def shutdown(self):
        super().shutdown()
        # rmv? self._pifacedigital.deinit_board()

class PiFaceDigital2SimulateCurrentSensor(DriverBase):
    _events_ = [KeyMasterSignals.CURRENT_FLOWING]
    def setup(self):
        super().setup()
        group_number = int(self.config.get('group_number', 0))
        init_board = self.config.get('init_board', False)
        self._pushbutton = int(self.config.get('pushbutton', 3-group_number))
        self._current_flowing = None
        self._pifacedigital = pifacedigitalio.PiFaceDigital(init_board=init_board)
    def startup(self):
        super().startup()
        self._publish_current_flowing(bool(self._pifacedigital.switches[self._pushbutton].value))
        self._listener = pifacedigitalio.InputEventListener(chip=self._pifacedigital)
        self._listener.register(self._pushbutton, pifacedigitalio.IODIR_FALLING_EDGE, self._button_clicked)
        self._listener.activate()
        self.open_for_business()
    def _button_clicked(self, event):
        self._publish_current_flowing(not self._current_flowing)
    def _publish_current_flowing(self, new_value):
        self._current_flowing = new_value
        self.publish(KeyMasterSignals.CURRENT_FLOWING, self._current_flowing)
        logger.info('published current flowing = {}'.format(self._current_flowing))
    def shutdown(self):
        self._listener.deactivate()
        super().shutdown()

