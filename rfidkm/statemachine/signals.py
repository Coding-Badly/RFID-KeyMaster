"""=============================================================================

  Signals for StateMachine.  This module contains the signals by the 
  StateMachine class.

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
import enum
import sys

class Signals(enum.IntEnum):
    GET_SUPER_STATE = enum.auto()
    INITIALIZE_STATE = enum.auto()
    ENTER_STATE = enum.auto()
    EXIT_STATE = enum.auto()
    TIMEOUT = enum.auto()
    LAST = enum.auto()

class StateMachineEvent():
    def __init__(self, signal, name=None):
        self.signal = signal
        self.name = name
    def __str__(self):
        if self.name:
            return self.name
        else:
            return str(self.signal)
    def __eq__(self, other):
        if isinstance(other, enum.IntEnum):
            return other.value == self.signal
        else:
            return super().__eq__(other)

def create_state_machine_events(an_enum, module_name):
    module = sys.modules[module_name]
    for e1 in an_enum:
        gn = 'EVENT_' + e1.name
        gv = StateMachineEvent(e1, gn)
        setattr(module, gn, gv)
