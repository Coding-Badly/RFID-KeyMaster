"""=============================================================================

  test_LoadableDriverLoader for RFID-KeyMaster.  Tests for
  LoadableDriverLoader.

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
from drivers.Auth.MemberDataFreshener import MemberDataFreshener
from drivers.DriverBase import DriverGroup, DeathOfRats
from exceptions import DriverClassNotFoundError
from utils.Configuration import Configuration
from utils.LoadableDriverLoader import LoadableDriverLoader
import json
import logging
import pytest

logger = logging.getLogger(__name__)

@pytest.fixture(scope="module")
def raw_config_002():
    return json.loads("""{
    "general": {
        "description": "Ping Pong",
        "revision": 1
    },
    "groups": ["primary"],
    "primary": [
        {
            "driver": "Ping1"
        },
        {
            "driver": "Pong2"
        }
    ]
}
""")

def test_001():
    tm1 = LoadableDriverLoader()
    with pytest.raises(DriverClassNotFoundError):
        tm2 = tm1.get_driver_class('nCxCWf8yZqVubuwQmyLpJ6k2')
    assert tm1['MemberDataFreshener'].driver_class == MemberDataFreshener
    assert tm1.get_driver_class('MemberDataFreshener') == MemberDataFreshener


def test_002(caplog, raw_config_002):
    caplog.set_level(logging.INFO)
    tm1 = LoadableDriverLoader()
    config = Configuration(raw_config_002)
    root = DriverGroup('root')
    dor = root.add(DeathOfRats(None))
    for group_name in config['groups']:
        group_root = root.add(DriverGroup(group_name))
        group_driver_list = config[group_name]
        for driver_config in group_driver_list:
            driver_name = driver_config['driver']
            logger.info(driver_config)
            driver_class = tm1.get_driver_class(driver_name)
