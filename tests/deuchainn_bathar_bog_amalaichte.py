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
from utils.Configuration import Configuration
from utils.LoadableDriverBuilder import LoadableDriverBuilder
import json
import logging
import pytest

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
            "poll_rate": 2.5
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

@pytest.fixture(scope="module")
def raw_config_002():
    return json.loads("""{
    "general": {
        "description": "Hardware Startup Check",
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
            "driver": "PiFaceDigital2Relays",
            "module": "PiFaceDigital2Interface"
        },
        {
            "driver": "HardwareStartupCheck"
        }
    ]
}
""")

#-----------------------------------------------------------------------------#

def test_001(caplog, raw_config_001, raw_config_002, raw_config_003):
    caplog.set_level(logging.INFO)
    tm1 = LoadableDriverBuilder(Configuration(raw_config_003))
    root = tm1.build()
    root.setup()
    root.start()
    root.join()
    root.teardown()

#-----------------------------------------------------------------------------#
#-----------------------------------------------------------------------------#
#-----------------------------------------------------------------------------#
