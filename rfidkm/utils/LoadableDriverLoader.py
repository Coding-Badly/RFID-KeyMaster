"""=============================================================================

  LoadableDriverLoader for RFID-KeyMaster.  LoadableDriverLoader locates and,
  on demand, loads modules from the drivers directory.

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
from importlib import import_module
import pathlib

from rfidkm.exceptions import DriverClassNameConflict, DriverClassNotFoundError

class LoadableDriverInformation():
    def __init__(self, relative_path, non_standard_class_name=None):
        self._relative_path = relative_path
        self._module_name, self._class_name = LoadableDriverInformation.convert_to_module_name_and_class_name(self._relative_path)
        if non_standard_class_name:
            self._class_name = non_standard_class_name
        self._driver_class = None
    def __hash__(self):
        return hash((self._class_name))
    def __eq__(self, other):
        return isinstance(other, LoadableDriverInformation) and (self._class_name == other._class_name)
    def __repr__(self):
        return 'LoadableDriverInformation({!r})'.format(self._relative_path)
    def __str__(self):
        return self._class_name
    @property
    def class_name(self):
        return self._class_name
    @property
    def module_name(self):
        return self._module_name
    @property
    def driver_class(self):
        if not self._driver_class:
            self._module = import_module(self.module_name)
            try:
                self._driver_class = getattr(self._module, self.class_name)
            except AttributeError:
                raise DriverClassNotFoundError(self.class_name)
        return self._driver_class
    @property
    def path(self):
        return self._relative_path
    @staticmethod
    def convert_to_module_name_and_class_name(relative_path):
        module_name = relative_path.stem
        class_name = module_name
        relative_path = relative_path.parent
        while relative_path.stem:
            module_name = relative_path.stem + '.' + module_name
            relative_path = relative_path.parent
        return (module_name, class_name)

class LoadableDriverLoader():
    def __init__(self):
        super().__init__()
        self._by_class_name = dict()
        l1 = list(LoadableDriverLoader.all_driver_paths())
        for rover in l1:
            di = LoadableDriverInformation(rover)
            self._by_class_name[di.class_name] = di
        if len(self._by_class_name) != len(l1):
            raise DriverClassNameConflict()
    def get_driver_class(self, class_name, module_name=None):
        driver_information = self._by_class_name.get(class_name, None)
        if not driver_information:
            if (module_name is None) or (class_name == module_name):
                raise DriverClassNotFoundError(class_name)
            driver_information = self._by_class_name.get(module_name, None)
            if not driver_information:
                raise DriverClassNotFoundError(class_name)
            di = LoadableDriverInformation(driver_information.path, class_name)
            self._by_class_name[di.class_name] = di
            driver_information = di
        return driver_information.driver_class
    @staticmethod
    def all_driver_paths():
        tp1 = pathlib.Path(__file__).parent.parent
        anchor = tp1.parent
        root = tp1 / 'drivers'
        driver_directories = [rover.parent for rover in root.glob('**/__init__.py') if rover.parent != root]
        for rover in driver_directories:
            for driver_path in rover.glob('*.py'):
                if driver_path.stem != '__init__':
                    rv1 = driver_path.relative_to(anchor)
                    yield rv1
