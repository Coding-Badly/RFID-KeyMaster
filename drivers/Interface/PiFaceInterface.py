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
from drivers.Interface import Interface
import pifacedigitalio
from exceptions.InvalidPositionException import InvalidPositionException
# rmv import atexit

class PiFaceInterface(Interface):
    def setup(self):
        super().setup()
        init_board = self.config.get('init_board', False)
        self._target = int(self.config.get('target', 0))
        # Turn off Interrupts
        pifacedigitalio.core.deinit()
        self.pifacedigital = pifacedigitalio.PiFaceDigital(init_board=init_board)
        self.subscribe(None, Interface.CONTROL_TARGET, self.receive_control_target)
        # rmv atexit.register(self.reset_piface)
        #return False
    def startup(self):
        super().startup()
        self.open_for_business()
    def receive_control_target(self, data):
        pass

    # rmv def reset_piface(self):
    # rmv     self.pifacedigital.init_board()

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
            return self.pifacedigital.input_pins[position-1].value

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
                self.pifacedigital.output_pins[position-1].turn_on()
            else:
                self.pifacedigital.output_pins[position-1].turn_off()
            return

        raise InvalidPositionException(
            "PiFace has no output position " + str(position))
