"""=============================================================================

  pytest for ADCacheRemote.
  
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

from drivers.Auth.ADCacheRemote import ADCacheAuth
from utils.twophaser import two_phase_open
import functools
import json
import logging
from pathlib import Path
import pytest

logger = logging.getLogger(__name__)

@pytest.fixture(scope='function', autouse=True)
def exit_pytest_first_failure(request):
    if request.session.testsfailed:
        pytest.exit('Stop on first failure.')

@pytest.fixture(scope="module", autouse=True)
def track_ADCache():
    filenames = [Path('ADCache.json'), Path('ADCache.json.bak')]
    any_existed = functools.reduce( lambda any_existed, path: any_existed or path.exists(), filenames, False )
    yield
    if not any_existed:
        for p1 in filenames:
            if p1.exists():
                p1.unlink()

def test_start_from_zero(caplog, request):
    caplog.set_level(logging.INFO)
    t1 = ADCacheAuth(None, None, None)
    with pytest.raises(FileNotFoundError):
        t1.loadCache()

def test_poisoned_cache():
    t1 = ADCacheAuth(None, None, None)
    with two_phase_open(t1.local_cache_file, 'wt') as ouf:
        pass
    with pytest.raises(json.decoder.JSONDecodeError):
        t1.loadCache()
    with two_phase_open(t1.local_cache_file, 'wt') as ouf:
        ouf.write("\n")
    with pytest.raises(json.decoder.JSONDecodeError):
        t1.loadCache()

def test_clean_cache():
    t1 = ADCacheAuth(None, None, None)
    with two_phase_open(t1.local_cache_file, 'wt') as ouf:
        ouf.write("""{
  "0000721130":
  {
    "user":
    {
      "fullName":"Brian Cook",
      "groups":["Laser 102 Zing Basics","Laser 101 Thunder Basics","VCC Instructors","Portainer Users","Machine Shop Sherline Lathe","Storage Bins","CA Vinyl Cutter","PRLXTOOLLOGS Admins","3D Printer NinjaFlex","CA Shapeoko Users","Woodshop Lathe Basics","Woodshop Multicam CNC Router","3D Printer Basics","Woodshop Basics","Laser Basics","Voting Members","CA DyeSub Printer","VCarve Users","Members"],
      "username":"roughvagabond"
    }
  }
}""")
    t1.loadCache()

