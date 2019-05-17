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
import pifacedigitalio
import logging

logger = logging.getLogger(__name__)

pifacedigitalio.core.init()

class PiFaceDigital2SimulateCurrentSensor(DriverBase):
    _events_ = [Signals.CURRENT_FLOWING]
    def setup(self):
        super().setup()
        self._current_flowing = False
        self._pifacedigital = pifacedigitalio.PiFaceDigital(init_board=False)
    def startup(self):
        super().startup()
        self._listener = pifacedigitalio.InputEventListener(chip=self._pifacedigital)
        self._listener.register(3, pifacedigitalio.IODIR_FALLING_EDGE, self._button_clicked)
        self._listener.activate()
        logger.info('{} open for business'.format(self.name))
        self.open_for_business()
    def _button_clicked(self, event):
        self._current_flowing = not self._current_flowing
        self.publish(Signals.CURRENT_FLOWING, self._current_flowing)
        logger.info('published current flowing = {}'.format(self._current_flowing))
    def shutdown(self):
        self._listener.deactivate()
        super().shutdown()

