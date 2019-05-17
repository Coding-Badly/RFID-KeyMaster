"""=============================================================================

  test_Configuration for RFID-KeyMaster.  test_Configuration contains pytest
  for Configuration.

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
import json
import logging
import pytest

logger = logging.getLogger(__name__)

@pytest.fixture(scope="module")
def raw_config_001():
    return json.loads("""{
    "general": {
        "description": "Automotive Lift #1",
        "revision": 1
    },
    "groups": ["primary"],
    "primary": [
        {
            "driver": "PiFaceDigital2Relays",
            "module": "PiFaceDigital2Interface",
            "init_board": false,
            "relay": 0
        },
        {
            "driver": "SycreaderUSB125",
            "reader": 0
        },
        {
            "driver": "MemberDataFreshener",
            "remote_cache_url": "https://www.rowdydogsoftware.com/TKRn2uZNBSCSBcTUPRFPhHBL/adcache.json",
            "poll_rate": 60.0
        }
    ]
}
""")

def test_001(caplog, raw_config_001):
    caplog.set_level(logging.INFO)
    config = Configuration(raw_config_001)
    root = DriverGroup('root')
    dor = root.add(DeathOfRats(config=config))
    for group_name in config['groups']:
        group_root = root.add(DriverGroup(group_name))
        group_driver_list = config[group_name]
        for driver_config in group_driver_list:
            driver_name = driver_config['driver']
            logger.info(driver_name)
