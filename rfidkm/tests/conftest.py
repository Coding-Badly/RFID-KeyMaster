"""=============================================================================

  Generic / general purpose fixtures for pytest.

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
from pathlib import Path
import pytest

import rfidkm.tests.exercise as exercise

def pytest_addoption(parser):
    parser.addoption(
        "--exercise_piface_relays", action="store_true", default=False, help="Toggle the two PiFace Digital 2 relays a few times."
    )
    parser.addoption(
        "--exercise_rfid_readers", action="store_true", default=False, help="Exercise all attached RFID readers."
    )
    parser.addoption(
        "--exercise_hardware", action="store_true", default=False, help="Exercise all the hardware that can be automatically identified."
    )

@pytest.fixture(scope="module")
def shared_data_path(request):
    base = Path(request.fspath.dirname)
    shared_data_path = base / 'data'
    return shared_data_path

# https://docs.pytest.org/en/latest/_modules/_pytest/tmpdir.html#TempPathFactory.mktemp
# ...search for "def tmp_path("
@pytest.fixture
def tmpdirn2(tmp_path):
    return Path(str(tmp_path))

@pytest.fixture(scope="module")
def config_MemberDataFreshener():
    return {'remote_cache_url':'https://www.rowdydogsoftware.com/TKRn2uZNBSCSBcTUPRFPhHBL/adcache.json','poll_rate':2.5}
    #return {'remote_cache_url':'https://www.rowdydogsoftware.com/TKRn2uZNBSCSBcTUPRFPhHBL/adcache.json'}

@pytest.fixture(scope="module")
def exercise_hardware(request):
    return request.config.getoption("--exercise_hardware")

@pytest.fixture(scope="module")
def exercise_piface_relays(request, exercise_hardware):
    rv = exercise_hardware or \
        request.config.getoption("--exercise_piface_relays")
    return rv

@pytest.fixture(scope="module")
def exercise_rfid_readers(request, exercise_hardware):
    rv = exercise_hardware or \
        request.config.getoption("--exercise_rfid_readers")
    return rv

def pytest_configure(config):
    if config.getoption("--exercise_hardware"):
        exercise.piface_relays = True
        exercise.rfid_readers = True
        exercise.hardware = True
    elif config.getoption("--exercise_piface_relays"):
        exercise.piface_relays = True
    elif config.getoption("--exercise_rfid_readers"):
        exercise.rfid_readers = True
