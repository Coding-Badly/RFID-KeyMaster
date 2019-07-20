"""=============================================================================

  Support for pytest.
  
  ----------------------------------------------------------------------------

  Copyright 2019 Brian Cook (aka Coding-Badly)

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
import os
import random
from pathlib import Path
import pytest
import pyzipper
import yaml

from rfidkm.utils.superglob import ENVIRONMENT_VARIABLE_PREFIX, clean_stem_to_simple_environment_variable

class EmployeeIDsBabbleFile():
    def __init__(self, shared_data_path, mode):
        self._shared_data_path = shared_data_path
        self._mode = mode
        self._path = None
        self._password = None
        self._zip = None
        self._stream = None
    def _init_part2(self):
        if self._path is None:
            self._path = self._shared_data_path / 'Employee IDs Babble.zip'
        if self._password is None:
            envarname = ENVIRONMENT_VARIABLE_PREFIX + clean_stem_to_simple_environment_variable(self._path.stem)
            self._password = os.getenv(envarname, None)
    def has_password(self):
        self._init_part2()
        return self._password is not None
    def __enter__(self):
        if not self.has_password():
            raise RuntimeError('No password available')
        self._zip = pyzipper.AESZipFile(
                self._path, 
                self._mode, 
                compression=pyzipper.ZIP_LZMA, 
                encryption=pyzipper.WZ_AES)
        self._zip.pwd = self._password
        self._stream = self._zip.open('Employee IDs Babble.yaml', self._mode)
        return self._stream
    def __exit__(self, exc_type, exc_value, traceback):
        if self._stream:
            self._stream.close()
            self._stream = None
        if self._zip:
            self._zip.close()
            self._zip = None
        return False

class RandomRFID():
    def babble(self):
        which = random.random()
        if which < 0.500:
            rv = '00'
            target = 10
        elif which >= 0.500 and which < 0.500+0.005:
            rv = '00'
            target = 9
        elif which >= 0.500+0.005 and which < 0.500+0.005+0.010:
            if random.random() < 0.500:
                rv = '0'
            else:
                rv = '1'
            target = 8
        elif which >= 0.500+0.005+0.010 and which < 0.500+0.005+0.010+0.200:
            rv = ''
            target = 7
        else:
            rv = ''
            target = 6
        while len(rv) < target:
            rv += chr(random.randrange(10)+ord('0'))
        return rv

@pytest.fixture(scope="module")
def employee_ids_babble(shared_data_path):
    read_this = EmployeeIDsBabbleFile(shared_data_path, 'r')
    if read_this.has_password():
        with read_this as stream:
            rv = yaml.full_load(stream)
    else:
        rv = RandomRFID()
    return rv

