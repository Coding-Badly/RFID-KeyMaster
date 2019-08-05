"""=============================================================================

  test_KeyMaster for RFID-KeyMaster.  This module exercises the code in 
  rfidkm/__init__.py.

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
import platform
import pytest

import rfidkm.tests.exercise as exercise

if not exercise.piface_relays:
    pytest.skip("skipping relay tests", allow_module_level=True)

if not exercise.rfid_readers:
    pytest.skip("skipping RFID reader tests", allow_module_level=True)

if platform.system() == 'Windows':
    pytest.skip("skipping tests that will not run on Windows", allow_module_level=True)

import json
import logging

import rfidkm
from rfidkm.utils.file_preserver import FilePreserver

logger = logging.getLogger(__name__)

@pytest.fixture
def converted_config_001():
    return json.loads("""{
    "general": {
        "description": "MemberDataFreshener for Loony Tunes",
        "revision": 1
    },
    "root": [
        {
            "driver": "BlackTagBringsDeathOfRats"
        }
    ],
    "groups": ["primary"],
    "primary": [
        {
            "driver": "MemberDataFreshener",
            "remote_cache_url": "https://www.rowdydogsoftware.com/TKRn2uZNBSCSBcTUPRFPhHBL/adcache.json",
            "poll_rate": 120.0
        },
        {
            "driver": "MemberDataCacher"
        },
        {
            "driver": "SycreaderUSB125"
        },
        {
            "driver": "BasicController"
        },
        {
            "driver": "PiFaceDigital2Relays",
            "module": "PiFaceDigital2Interface"
        },
        {
            "driver": "Authenticator"
        },
        {
            "driver": "Authorizer",
            "groups": [["Automotive 102 (Lift Training)","power"]]
        }
    ]
}
""")

def do_it(converted_config, url_to_use, temporary_directory, expect_success):
    if url_to_use:
        converted_config["primary"][0]["remote_cache_url"] = url_to_use
    config_path = temporary_directory / 'key_master.json'
    with config_path.open('w') as ouf:
        json.dump(converted_config, ouf)
    tm1 = rfidkm.KeyMaster()
    tm2 = tm1.build_from_configuration_file(config_path)
    assert tm2 == converted_config  # rmv
    mdc = tm1._root.find_driver_by_name('MemberDataCacher')
    mdp1 = mdc.get_path()
    mdp2 = mdp1.parent / (mdp1.name + '.bak')
    with FilePreserver(mdp1, mdp2):
        assert not mdp1.exists()
        assert not mdp2.exists()
        tm1.setup_and_start()
        tm1.wait_for_stop()
        if expect_success:
            assert mdp1.exists()
        else:
            assert not mdp1.exists()

def test_001(caplog, tmpdirn2, converted_config_001):
    caplog.set_level(logging.INFO)
    do_it(converted_config_001, None, tmpdirn2, True)

def fix_test_002(caplog, tmpdirn2, converted_config_001):
    caplog.set_level(logging.INFO)
    do_it(converted_config_001, "https://httpstat.us/404", tmpdirn2, False)

def fix_test_003(caplog, tmpdirn2, converted_config_001):
    caplog.set_level(logging.INFO)
    do_it(converted_config_001, "https://httpstat.us/200", tmpdirn2, False)

def fix_test_004(caplog, tmpdirn2, converted_config_001):
    caplog.set_level(logging.INFO)
    do_it(converted_config_001, "https://t5jdR9uj5dnw3ax8wjrhnzvV.urp", tmpdirn2, False)

def fix_test_005(caplog, tmpdirn2, converted_config_001):
    caplog.set_level(logging.INFO)
    do_it(converted_config_001, "https://172.31.255.1", tmpdirn2, False)

@pytest.fixture
def converted_config_power_control():
    return json.loads("""{
    "general": {
        "description": "Example Configuration for Power Control",
        "revision": 1
    },
    "groups": ["primary"],
    "root": [
        {
            "driver": "BlackTagBringsDeathOfRats"
        }
    ],
    "primary": [
        {
            "driver": "PiFaceDigital2Relays",
            "module": "PiFaceDigital2Interface"
        },
        {
            "driver": "Authenticator"
        },
        {
            "driver": "Authorizer",
            "groups": [["Woodshop Lathe Basics"]]
        },
        {
            "driver": "MemberDataFreshener",
            "remote_cache_url": "https://www.rowdydogsoftware.com/TKRn2uZNBSCSBcTUPRFPhHBL/adcache.json",
            "poll_rate": 120.0
        },
        {
            "driver": "MemberDataCacher"
        }
    ]
}
""")

"""
        {
            "driver": "SycreaderUSB125"
        },
        {
            "driver": "PiFaceDigital2SimulateCurrentSensor",
            "module": "PiFaceDigital2Interface"
        },
        {
            "driver": "PowerController"
        },
"""
