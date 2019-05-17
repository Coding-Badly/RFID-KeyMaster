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
from drivers import Signals
from drivers.DriverBase import DriverBase
import pifacedigitalio
# rmv import atexit
import logging

logger = logging.getLogger(__name__)

# Required for the board to function correctly.
pifacedigitalio.core.init()

class PiFaceDigital2Relays(DriverBase):
    def setup(self):
        super().setup()
        group_number = int(self.config.get('group_number', 0))
        init_board = self.config.get('init_board', False)
        self._relay = int(self.config.get('relay', group_number))
        # Turn off Interrupts
        # rmv? pifacedigitalio.core.deinit()
        self._pifacedigital = pifacedigitalio.PiFaceDigital(init_board=init_board)
        self.subscribe(None, Signals.CONTROL_TARGET, self.receive_control_target)
        # rmv atexit.register(self.reset_piface)
        #return False
    def startup(self):
        super().startup()
        # fix? Publish the initial state of the target?
        self.open_for_business()
    def receive_control_target(self, data):
        new_value = int(data)
        self._pifacedigital.relays[self._relay].value = new_value
        # fix? Publish that the target state has changed?
        logger.info('relay set to = {}'.format(new_value))
    def shutdown(self):
        super().shutdown()
        # rmv? self._pifacedigital.deinit_board()

class PiFaceDigital2SimulateCurrentSensor(DriverBase):
    _events_ = [Signals.CURRENT_FLOWING]
    def setup(self):
        super().setup()
        group_number = int(self.config.get('group_number', 0))
        init_board = self.config.get('init_board', False)
        self._pushbutton = int(self.config.get('relay', 3-group_number))
        self._current_flowing = False
        self._pifacedigital = pifacedigitalio.PiFaceDigital(init_board=init_board)
    def startup(self):
        super().startup()
        self._listener = pifacedigitalio.InputEventListener(chip=self._pifacedigital)
        self._listener.register(3, pifacedigitalio.IODIR_FALLING_EDGE, self._button_clicked)
        self._listener.activate()
        self.open_for_business()
    def _button_clicked(self, event):
        self._current_flowing = not self._current_flowing
        self.publish(Signals.CURRENT_FLOWING, self._current_flowing)
        logger.info('published current flowing = {}'.format(self._current_flowing))
    def shutdown(self):
        self._listener.deactivate()
        super().shutdown()

