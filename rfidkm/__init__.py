"""=============================================================================

  Entry point for the RFID-KeyMaster package.

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
import json

from rfidkm.utils.Configuration import Configuration
from rfidkm.utils.LoadableDriverBuilder import LoadableDriverBuilder

# cls & pytest rfidkm/tests/test_KeyMaster.py

class KeyMaster():
    __slots__ = ['_root', '_is_running']
    def __init__(self):
        self._root = None
        self._is_running = False
    def build_from_loaded_json(self, converted_config):
        assert self._root is None
        wrapped_config = Configuration(converted_config)
        config_builder = LoadableDriverBuilder(wrapped_config)
        self._root = config_builder.build()
    def build_from_configuration_file(self, config_path):
        with config_path.open('r') as inf:
            converted_config = json.load(inf)
        self.build_from_loaded_json(converted_config)
        return converted_config  # rmv
    def setup_and_start(self):
        if not self._is_running:
            self._root.setup()
            self._root.start()
            self._is_running = True
    def wait_for_stop(self):
        if self._is_running:
            self._root.join()
            self._root.teardown()
            self._is_running = False
    #def make_power_controller(self, group_name):
    #    pass

"""
import json

json.loads("")

    tm1 = LoadableDriverBuilder(Configuration(raw_config_001))
    root = tm1.build()
    root.setup()
    root.start()
    root.join()
    root.teardown()

        tm1 = LoadableDriverBuilder(Configuration(raw_config))
        raw_config['primary'][2]['expected_current_was_flowing'] = expected_current_was_flowing
        raw_config['primary'][2]['expected_relay_was_closed'] = expected_relay_was_closed
        root = tm1.build()
        root.setup()
        root.start()
        root.join()
        root.teardown()

    config = Configuration(raw_config_001)
    root = DriverGroup('root')
    dor = root.add(DeathOfRats(config=config))
    for group_name in config['groups']:
        group_root = root.add(DriverGroup(group_name))
        group_driver_list = config[group_name]
        for driver_config in group_driver_list:
            driver_name = driver_config['driver']
            logger.info(driver_name)

C:\ProjectsSplit\Make\RFID-KeyMaster\rfidkm\tests\test_LoadableDriverLoader.py

C:\ProjectsSplit\Make\RFID-KeyMaster\rfidkm\tests\test_MemberDataFreshener.py
"""
