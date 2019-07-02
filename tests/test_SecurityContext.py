"""=============================================================================

  test_SecurityContext for RFID-KeyMaster.  test_SecurityContext is a pytest
  module for SecurityContext.

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
from utils.securitycontext import Permission, Group, SecurityContext
import logging

logger = logging.getLogger(__name__)

def test_Permission():
    p11 = Permission('one')
    p12 = Permission('one', 'The first one.')
    assert p11 == p12
    assert hash(p11) == hash(p12)
    assert p11._get_init_tuple() == ('one',None)
    assert p12._get_init_tuple() == ('one','The first one.')
    p21 = Permission('two')
    assert p11 != p21
    assert hash(p11) != hash(p21)

def test_Group():
    g11 = Group('one')
    g12 = Group('one')
    assert g11 == g12
    assert hash(g11) == hash(g12)
    assert g11._get_init_tuple() == ('one',)

def test_SecurityContext(caplog):
    caplog.set_level(logging.INFO)
    tm1 = SecurityContext()
    tm2 = SecurityContext()
    assert tm1 == tm2
    p11 = tm1.add_permission('power', 'User can enable power for the tool.')
    p12 = tm1.add_permission('power', 'Whatever.')
    p11 == p12
    Permission('power') == p11
    p21 = tm2.add_permission('power', 'User can enable power for the tool.')
    p22 = tm2.add_permission('power', 'Whatever.')
    assert tm1 == tm2
    p11 = tm1.add_permission('unlock', 'User can release the latch to gain access.')
    p12 = tm1.add_permission('unlock', 'Whatever.')
    p11 == p12
    Permission('unlock') == p11
    p21 = tm2.add_permission('unlock', 'User can release the latch to gain access.')
    p22 = tm2.add_permission('unlock', 'Whatever.')
    assert tm1 == tm2
    g11 = tm1.add_group('Automotive 102 (Lift Training)')
    g12 = tm1.add_group('Automotive 102 (Lift Training)')
    assert g11 == g12
    assert Group('Automotive 102 (Lift Training)') == g11
    g21 = tm2.add_group('Automotive 102 (Lift Training)')
    g22 = tm2.add_group('Automotive 102 (Lift Training)')
    assert tm1 == tm2
    g13 = tm1.add_group('Automotive 102 (Lift Training)', 'power')
    assert g11 == g13
    assert tm1 != tm2
    g23 = tm2.add_group('Automotive 102 (Lift Training)', 'power')
    assert g21 == g23
    assert tm1 == tm2
    #
    tm1 = SecurityContext(permissions={})
    tm2 = SecurityContext()
    assert tm1 == tm2
    tm1 = SecurityContext(permissions={'power':'User can enable power for the tool.', 'unlock':'User can release the latch to gain access.'})
    tm2 = SecurityContext()
    tm2.add_permission('unlock','Whatever.')
    tm2.add_permission('power','On/off switch.')
    assert tm1 == tm2
    tm1 = SecurityContext(permissions='unlock')
    tm2 = SecurityContext()
    tm2.add_permission('unlock','Whatever.')
    assert tm1 == tm2
    tm1 = SecurityContext(permissions=('unlock',''))
    assert tm1 == tm2
    tm1 = SecurityContext(permissions=(('unlock','Use key.'),('power','On/off switch.')))
    tm2.add_permission('power','On/off switch.')
    assert tm1 == tm2
    tm1 = SecurityContext(permissions=[('unlock','Use key.'),('power','On/off switch.')])
    assert tm1 == tm2
    #
    tm1 = SecurityContext(groups={})
    tm2 = SecurityContext()
    assert tm1 == tm2
    tm1 = SecurityContext(groups={'small':'power', 'large':'power'})
    tm2 = SecurityContext()
    tm2.add_permission('power','On/off switch.')
    tm2.add_group('small', 'power')
    tm2.add_group('large', 'power')
    assert tm1 == tm2
    tm1 = SecurityContext(groups={'small':['power'], 'large':['power','unlock']})
    tm2 = SecurityContext()
    tm2.add_permission('power','On/off switch.')
    tm2.add_permission('unlock','Have the key.')
    tm2.add_group('small', ['power'])
    tm2.add_group('large', ['unlock','power'])
    assert tm1 == tm2
    tm1 = SecurityContext(groups='small')
    tm2 = SecurityContext()
    tm2.add_group('small', [])
    assert tm1 == tm2
    tm1 = SecurityContext(groups=('small','power'))
    tm2 = SecurityContext()
    tm2.add_permission('power','On/off switch.')
    tm2.add_group('small', ['power'])
    assert tm1 == tm2
    tm1 = SecurityContext(groups=(('small','power'),('large',['power','unlock'])))
    tm2 = SecurityContext()
    tm2.add_permission('unlock','Use the key.')
    tm2.add_permission('power','On/off switch.')
    tm2.add_group('small', ['power'])
    tm2.add_group('large', ['unlock','power'])
    assert tm1 == tm2
    tm1 = SecurityContext(groups=[
            ('small','power'),
            ('large',['power','unlock'])])
    assert tm1 == tm2
