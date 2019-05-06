"""=============================================================================

  freshen_member_data for RFID-KeyMaster.  freshen_member_data is used to
  update the member data cache file using the RFID-KeyMaster application.
  freshen_member_data is meant to be run explicitely from pytest.

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
import logging

logger = logging.getLogger(__name__)

def test_freshen_member_data(caplog, config_MemberDataFreshener):
    caplog.set_level(logging.INFO)
    root = DriverGroup('root')
    mdc = root.add(MemberDataCacher('Member Data Cacher', None, None, None))
    mdf = root.add(MemberDataFreshener('Member Data Freshner', config_MemberDataFreshener, None, None))
    dor = root.add(RunForSeconds(5.0))
    root.setup()
    root.start()
    root.join()
    root.teardown()

