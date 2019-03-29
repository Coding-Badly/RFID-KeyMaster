"""=============================================================================

  Loadable for RFID-KeyMaster.  Loadable is a base class for all run-time
  loadable drivers.  Each Loadable is also a Thread allowing it to block
  without interfering with other parts of the application.  Loadable provides
  three services: 1. Connection to configuration data and a parent; 2. Find
  siblings so drivers can interact directly with each other; 3. Turn all
  unexpected exceptions into a clean exit.
  
  ----------------------------------------------------------------------------

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
from threading import Thread
from exceptions.RequiredDriverException import RequiredDriverException
import logging
import os
from pydispatch import Dispatcher

class Loadable(Thread, Dispatcher):
    def __init__(self, config, loader, id):
        self.config = config
        self.loader = loader
        self.id = id
        super().__init__()

    def setup(self):
        return False

    def getDriver(self, driver_name, controller=None):
        driver = self.loader.getDriver(driver_name, controller)
        if driver == None:
            raise RequiredDriverException(driver_name)  
        return driver  

    def run(self):
        self.startup = True
        try:
            while self.loop() != False:
                self.startup = False
        except Exception as e:
            logging.error("Exception: %s" % str(e), exc_info=1)
            os._exit(42) # Make sure entire application exits

    def loop(self):
        return False

