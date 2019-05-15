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
from drivers.Test.Ping import Ping1, Ping2
from drivers.Test.RunForSeconds import RunForSeconds
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
            "driver": "Ping1",
            "module": "Ping"
        },
        {
            "driver": "Pong1",
            "module": "Pong"
        }
    ]
}
""")

def test_001():
    tm1 = LoadableDriverLoader()
    with pytest.raises(DriverClassNotFoundError):
        tm2 = tm1.get_driver_class('nCxCWf8yZqVubuwQmyLpJ6k2')
    with pytest.raises(DriverClassNotFoundError):
        tm1.get_driver_class('e6RaapmY353pn7BdS5E7ZDZ4', 'GgqJm9HTHyVESYa3PuRFSkFn')
    with pytest.raises(DriverClassNotFoundError):
        tm1.get_driver_class('vUJ6MekXXF4EfhsaYQmk8cHg', 'Ping')
    with pytest.raises(DriverClassNotFoundError):
        tm1.get_driver_class('Ping1', 'BXRwWQtF9td5RuNdQMWk5yuK')
    assert tm1.get_driver_class('MemberDataFreshener') == MemberDataFreshener
    assert tm1.get_driver_class('Ping1', 'Ping') == Ping1
    assert tm1.get_driver_class('Ping2', 'Ping') == Ping2

def create_drivers_from_branch(loader, group_anchor, group_driver_list):
    for driver_config in group_driver_list:
        driver_name = driver_config['driver']
        module_name = driver_config.get('module', None)
        driver_class = loader.get_driver_class(driver_name, module_name)
        group_anchor.add(driver_class(driver_config))
    return len(group_driver_list) > 0

def create_branch_from_config(loader, anchor, config, group_name_list):
    for group_name in group_name_list:
        group_driver_list = config.get(group_name, None)
        group_anchor = anchor.add(DriverGroup(group_name))
        create_drivers_from_branch(loader, group_anchor, group_driver_list)

def test_002(caplog, raw_config_002):
    caplog.set_level(logging.INFO)
    loader = LoadableDriverLoader()
    config = Configuration(raw_config_002)
    root = DriverGroup('root')
    if not create_drivers_from_branch(loader, root, config['root']):
        dor = root.add(DeathOfRats(None))
    create_branch_from_config(loader, root, config, config['groups'])
    # rmv for group_name in config['groups']:
    # rmv     group_root = root.add(DriverGroup(group_name))
    # rmv     group_driver_list = config[group_name]
    # rmv     for driver_config in group_driver_list:
    # rmv         driver_name = driver_config['driver']
    # rmv         module_name = driver_config.get('module', None)
    # rmv         driver_class = loader.get_driver_class(driver_name, module_name)
    # rmv         group_root.add(driver_class(driver_config))
    root.setup()
    root.start()
    root.join()
    root.teardown()
