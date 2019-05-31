"""=============================================================================

  Signals for RFID-KeyMaster.  This module contains all the signals used in the
  KeyMaster application.  Signals are placed here instead of spread throughout
  to make maintenance and documentation easier.

  ----------------------------------------------------------------------------

  Copyright 2019 Mike Cole (aka @Draco, MikeColeGuru)
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
from enum import IntEnum, auto

class Signals(IntEnum):
    GET_SUPER_STATE = auto()
    INITIALIZE_STATE = auto()
    ENTER_STATE = auto()
    EXIT_STATE = auto()
    STOP_NOW = auto()
    FIRST_USER_DEFINED = auto()

class KeyMasterSignals(IntEnum):
    FIRST = Signals.FIRST_USER_DEFINED
    CONTROL_TARGET = auto()
    TARGET_ENGAGED = auto()
    SWIPE_10 = auto()
    FRESH_DATA = auto()
    CACHED_DATA = auto()
    USER_LOGGED_IN = auto()
    USER_LOGGED_OUT = auto()
    USER_LOGIN_FAILED = auto()
    USER_AUTHORIZED = auto()
    CURRENT_FLOWING = auto()
    LAST = auto()

# rmv LOGIN_RFID_NOT_FOUND        = 'login_rfid_not_found'
# rmv LOGIN_PERMISSION_DENIED     = 'login_permission_denied'
# rmv LOGIN_SUCCESS               = 'login_success'
