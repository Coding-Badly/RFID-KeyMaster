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
import enum
from ..statemachine import Signals, StateMachineEvent

class DriverSignals(enum.IntEnum):
    FIRST = Signals.LAST
    STOP_NOW = enum.auto()
    LAST = enum.auto()

class KeyMasterSignals(enum.IntEnum):
    FIRST = DriverSignals.LAST
    CONTROL_RELAY = enum.auto()
    RELAY_CLOSED = enum.auto()
    SWIPE_10 = enum.auto()
    FRESH_DATA = enum.auto()
    CACHED_DATA = enum.auto()
    USER_LOGGED_IN = enum.auto()
    USER_LOGGED_OUT = enum.auto()
    USER_LOGIN_FAILED = enum.auto()
    USER_AUTHORIZED = enum.auto()
    USER_FINISHED = enum.auto()
    USER_DENIED = enum.auto()
    CURRENT_FLOWING = enum.auto()
    LAST = enum.auto()

class UserAuthorizedEvent(StateMachineEvent):
    def __init__(self, id):
        super().__init__(KeyMasterSignals.USER_AUTHORIZED, None)
        self.id = id

class UserDeniedEvent(StateMachineEvent):
    def __init__(self, id):
        super().__init__(KeyMasterSignals.USER_DENIED, None)
        self.id = id

class UserFinishedEvent(StateMachineEvent):
    def __init__(self, id):
        super().__init__(KeyMasterSignals.USER_FINISHED, None)
        self.id = id

