"""=============================================================================

  Configuration for RFID-KeyMaster.  Configuration is a wrapper around a JSON
  document intended to be configuration data.  Configuration does some cleanup
  and provides some utility methods.

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
from collections import UserDict

class Configuration(UserDict):
    def __init__(self, initial_data):
        t1 = Configuration.make_keys_lower(initial_data)
        t1['groups'] = frozenset(group.lower() for group in t1.get('groups',{}))
        super().__init__(t1)
    def get_by_path(self, path, default=None):
        if isinstance(path, str):
            value = self.get(path, StopIteration)
            if value == StopIteration:
                return default
            else:
                return value
        else:
            rover = self
            for item in path:
                value = rover.get(item, StopIteration)
                if value == StopIteration:
                    return default
                rover = value
            return rover
    @staticmethod
    def make_keys_lower(root):
        rv = dict()
        for key, value in root.items():
            if isinstance(value, dict):
                value = Configuration.make_keys_lower(value)
            rv[key.lower()] = value
        return rv

