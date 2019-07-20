"""=============================================================================

  deuchainn_bathar_bog_amalaichte.py for RFID-KeyMaster.  Integrated software
  test.

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
import logging
import pifacedigitalio
import pytest
import readline

from rfidkm.utils.Configuration import Configuration
from rfidkm.utils.LoadableDriverBuilder import LoadableDriverBuilder

logger = logging.getLogger(__name__)

#-----------------------------------------------------------------------------#

@pytest.fixture(scope="module")
def raw_config_001():
    return json.loads("""{
    "general": {
        "description": "Click on Swipe",
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
            "poll_rate": 60.0
        },
        {
            "driver": "MemberDataCacher"
        },
        {
            "driver": "SycreaderUSB125"
        },
        {
            "driver": "PiFaceDigital2SimulateCurrentSensor",
            "module": "PiFaceDigital2Interface"
        },
        {
            "driver": "Authenticator"
        },
        {
            "driver": "Authorizer",
            "groups": [["Voting Members","power"]]
        },
        {
            "driver": "PowerController"
        },
        {
            "driver": "PiFaceDigital2Relays",
            "module": "PiFaceDigital2Interface"
        }
    ]
}
""")

def test_001_001(caplog, raw_config_001):
    caplog.set_level(logging.INFO)
    tm1 = LoadableDriverBuilder(Configuration(raw_config_001))
    root = tm1.build()
    root.setup()
    root.start()
    root.join()
    root.teardown()

#-----------------------------------------------------------------------------#

@pytest.fixture(scope="module")
def raw_config_002():
    return json.loads("""{
    "general": {
        "description": "Simulate Current Sensor",
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
            "driver": "SycreaderUSB125"
        },
        {
            "driver": "PiFaceDigital2SimulateCurrentSensor",
            "module": "PiFaceDigital2Interface"
        }
    ]
}
""")

#-----------------------------------------------------------------------------#

@pytest.fixture
def raw_config_003():
    return json.loads("""{
    "general": {
        "description": "Hardware Startup Check",
        "revision": 1
    },
    "groups": ["primary"],
    "primary": [
        {
            "driver": "SycreaderUSB125"
        },
        {
            "driver": "PiFaceDigital2SimulateCurrentSensor",
            "module": "PiFaceDigital2Interface"
        },
        {
            "driver": "HardwareStartupCheck",
            "expected_current_was_flowing": false,
            "expected_relay_was_closed": false
        },
        {
            "driver": "PiFaceDigital2Relays",
            "module": "PiFaceDigital2Interface"
        }
    ]
}
""")

#-----------------------------------------------------------------------------#

def pause_test(pytestconfig, text):
    capmanager = pytestconfig.pluginmanager.getplugin('capturemanager')
    capmanager.suspend_global_capture(in_=True)
    j1 = input(text)
    capmanager.resume_global_capture()

def run_one(pytestconfig, raw_config, expected_current_was_flowing, expected_relay_was_closed):
    if expected_current_was_flowing:
        pause_test(pytestconfig, "Hold S3 then press Enter...")
    else:
        pause_test(pytestconfig, "Release S3 then press Enter...")
    _pifacedigital = pifacedigitalio.PiFaceDigital(init_board=False)
    _pifacedigital.relays[0].value = expected_relay_was_closed
    try:
        tm1 = LoadableDriverBuilder(Configuration(raw_config))
        raw_config['primary'][2]['expected_current_was_flowing'] = expected_current_was_flowing
        raw_config['primary'][2]['expected_relay_was_closed'] = expected_relay_was_closed
        root = tm1.build()
        root.setup()
        root.start()
        root.join()
        root.teardown()
    finally:
        _pifacedigital.relays[0].value = False

def x_test_003_001(caplog, pytestconfig, raw_config_003):
    caplog.set_level(logging.INFO)
    run_one(pytestconfig, raw_config_003, False, False)

def x_test_003_002(caplog, pytestconfig, raw_config_003):
    caplog.set_level(logging.INFO)
    run_one(pytestconfig, raw_config_003, False, True)

def x_test_003_003(caplog, pytestconfig, raw_config_003):
    caplog.set_level(logging.INFO)
    run_one(pytestconfig, raw_config_003, True, False)

def x_test_003_004(caplog, pytestconfig, raw_config_003):
    caplog.set_level(logging.INFO)
    run_one(pytestconfig, raw_config_003, True, True)

#-----------------------------------------------------------------------------#
#-----------------------------------------------------------------------------#
#-----------------------------------------------------------------------------#