"""=============================================================================

  pytest for KeyboardRFID.
  
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
import platform
import pytest

if platform.system() == 'Windows':
    pytest.skip("skipping tests that will not run on Windows", allow_module_level=True)

from drivers.RFID.KeyboardRFID import KeyboardRFID

def test_simple_construction(exercise_rfid_readers):
    if exercise_rfid_readers:
        tm1 = KeyboardRFID(None, None, None)
