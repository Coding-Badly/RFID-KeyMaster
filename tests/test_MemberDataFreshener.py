"""=============================================================================

  test_MemberDataFreshener for RFID-KeyMaster.  test_MemberDataFreshener
  exercises MemberDataFreshener.

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
from utils.file_preserver import FilePreserver
from utils.LoadableDriverBuilder import LoadableDriverBuilder
import json
import logging
import pytest

logger = logging.getLogger(__name__)

@pytest.fixture
def raw_config_001():
    return json.loads("""{
    "general": {
        "description": "MemberDataFreshener for Loony Tunes",
        "revision": 1
    },
    "root": [
        {
            "driver": "RunForSeconds",
            "seconds": 10.0
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
        }
    ]
}
""")

def do_it(config, url_to_use, expect_success):
    if url_to_use:
        config["primary"][0]["remote_cache_url"] = url_to_use
    tm1 = LoadableDriverBuilder(Configuration(config))
    root = tm1.build()
    mdc = root.find_driver_by_name('MemberDataCacher')
    mdp1 = mdc.get_path()
    mdp2 = mdp1.parent / (mdp1.name + '.bak')
    with FilePreserver(mdp1, mdp2):
        assert not mdp1.exists()
        assert not mdp2.exists()
        root.setup()
        root.start()
        root.join()
        root.teardown()
        if expect_success:
            assert mdp1.exists()
        else:
            assert not mdp1.exists()

def test_001(caplog, raw_config_001):
    caplog.set_level(logging.INFO)
    do_it(raw_config_001, None, True)

def test_002(caplog, raw_config_001):
    caplog.set_level(logging.INFO)
    do_it(raw_config_001, "https://httpstat.us/404", False)

def test_003(caplog, raw_config_001):
    caplog.set_level(logging.INFO)
    do_it(raw_config_001, "https://httpstat.us/200", False)

def test_004(caplog, raw_config_001):
    caplog.set_level(logging.INFO)
    do_it(raw_config_001, "https://t5jdR9uj5dnw3ax8wjrhnzvV.urp", False)

def test_005(caplog, raw_config_001):
    caplog.set_level(logging.INFO)
    do_it(raw_config_001, "https://172.31.255.1", False)

