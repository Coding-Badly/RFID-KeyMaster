"""=============================================================================

  test_MemberDataCacher for RFID-KeyMaster.  test_MemberDataCacher is a pytest
  module for MemberDataCacher.

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
from drivers.Auth.MemberDataCacher import MemberDataCacher
from drivers.Auth.MemberDataFreshener import MemberDataFreshener
from drivers.DriverBase import DriverGroup
from drivers.Test.RunForSeconds import RunForSeconds
import json
from utils import get_cache_path
from utils.file_preserver import FilePreserver
import logging
import pytest

logger = logging.getLogger(__name__)

@pytest.fixture(scope="module")
def interval_duration():
    return 10.0
    #return None

def prepare_member_data_group(config_MemberDataFreshener, run_for_seconds = None):
    run_for_seconds = run_for_seconds if run_for_seconds else 60.0*60.0
    root = DriverGroup('root')
    mdc = root.add(MemberDataCacher(None))
    mdf = root.add(MemberDataFreshener(config_MemberDataFreshener))
    dor = root.add(RunForSeconds({'seconds':run_for_seconds}))
    mdp1 = mdc.get_path()
    mdp2 = mdp1.parent / (mdp1.name + '.bak')
    return (root, mdp1, mdp2)

def run_root(root):
    root.setup()
    root.start()
    root.join()
    root.teardown()

def test_interval(caplog, config_MemberDataFreshener, interval_duration):
    caplog.set_level(logging.INFO)
    logger.info('Part 1...')
    root, mdp1, mdp2 = prepare_member_data_group(config_MemberDataFreshener, interval_duration)
    with FilePreserver(mdp1, mdp2):
        assert not mdp1.exists()
        assert not mdp2.exists()
        run_root(root)
        assert mdp1.exists()
        logger.info('Part 2...')
        root, junk1, junk2 = prepare_member_data_group(config_MemberDataFreshener, interval_duration)
        run_root(root)
        assert mdp1.exists()
        assert mdp2.exists()

