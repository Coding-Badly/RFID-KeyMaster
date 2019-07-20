"""=============================================================================

  pytest for DriverBaseOld.

  ----------------------------------------------------------------------------

  Copyright 2019 Brian Cook (aka Coding-Badly)

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
import pytest

from rfidkm.drivers.DriverBase import DriverBaseOld
from rfidkm.exceptions.RequiredDriverException import RequiredDriverException

class LoaderStub1():
    def getDriver(self, driver_name, controller):
        return None

class SiblingStub2():
    pass

class LoaderStub2():
    def getDriver(self, driver_name, controller):
        if driver_name == 'sibling':
            return SiblingStub2()
        else:
            return None

def test_simple_construction():
    tm1 = DriverBaseOld(None, None, None)

def rmv_test_stubs():
    tm1 = DriverBaseOld(None, None, None)
    assert tm1.setup() == False
    assert tm1.loop() == False

def test_no_loader():
    tm1 = DriverBaseOld(None, None, None)
    with pytest.raises(AttributeError):
        tm1.getDriver('whatever')

def test_no_sibling():
    tm1 = DriverBaseOld(None, LoaderStub1(), None)
    with pytest.raises(RequiredDriverException):
        tm1.getDriver('whatever')

def test_have_sibling():
    tm1 = DriverBaseOld(None, LoaderStub2(), None)
    tm2 = tm1.getDriver('sibling')
    assert isinstance(tm2, SiblingStub2)

def test_run():
    tm1 = DriverBaseOld(None, LoaderStub2(), None)
    tm1.start()
    tm1.join()
    assert not tm1.is_alive()
    # rmv assert tm1.startup == True

