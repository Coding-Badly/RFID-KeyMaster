"""=============================================================================

  PiFaceInterface for RFID-KeyMaster.  PiFaceInterface is a driver for the
  PiFace Digital 2 HAT.  The PiFace is used to control power to the target,
  receive input from a pushbutton, and drive an LED.

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
from exceptions.InvalidPositionException import InvalidPositionException
import pifacedigitalio
# rmv import atexit
import logging

logger = logging.getLogger(__name__)

class PiFaceInterface(DriverBase):
    def setup(self):
        super().setup()
        group_number = int(self.config.get('group_number', 0))
        init_board = self.config.get('init_board', True)
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
    def shutdown(self):
        super().shutdown()
        # rmv? self._pifacedigital.deinit_board()

    # rmv def reset_piface(self):
    # rmv     self._pifacedigital.init_board()

    def relay(self, position, value):
        position = int(position)

        if position >= 1 and position <= 2:
            self.output(position, value)
            return

        raise InvalidPositionException(
            "Pyface has no relay position " + str(position))

    def input(self, position):
        position = int(position)

        if position >= 1 and position <= 8:
            return self._pifacedigital.input_pins[position-1].value

        raise InvalidPositionException(
            "PiFace has no input position " + str(position))

    def output(self, position, value):
        position = int(position)

        if value:
            value = 1
        else:
            value = 0

        if position >= 1 and position <= 8:
            if value:
                self._pifacedigital.output_pins[position-1].turn_on()
            else:
                self._pifacedigital.output_pins[position-1].turn_off()
            return

        raise InvalidPositionException(
            "PiFace has no output position " + str(position))
