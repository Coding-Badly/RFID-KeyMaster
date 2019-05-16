"""=============================================================================

  LoadableDriverBuilder for RFID-KeyMaster.  LoadableDriverBuilder brings
  Configuration and LoadableDriverLoader together to build a ready-to-run
  driver tree.

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
from drivers.DriverBase import DriverGroup, DeathOfRats
from utils.Configuration import Configuration
from utils.LoadableDriverLoader import LoadableDriverLoader

class LoadableDriverBuilder():
    def __init__(self, config, loader=None):
        super().__init__()
        self._config = config
        self._loader = loader if loader else LoadableDriverLoader()
    def build(self):
        root = DriverGroup('root')
        if not self.create_drivers_from_list(root, self._config['root']):
            dor = root.add(DeathOfRats(None))
        self.create_tree_from_config(root)
        return root
    def create_drivers_from_list(self, group_anchor, group_driver_list):
        for driver_config in group_driver_list:
            driver_name = driver_config['driver']
            module_name = driver_config.get('module', None)
            driver_class = self._loader.get_driver_class(driver_name, module_name)
            group_anchor.add(driver_class(driver_config))
        return len(group_driver_list) > 0
    def create_tree_from_config(self, anchor):
        for group_name in self._config['groups']:
            group_driver_list = self._config.get(group_name, None)
            group_anchor = anchor.add(DriverGroup(group_name))
            self.create_drivers_from_list(group_anchor, group_driver_list)
