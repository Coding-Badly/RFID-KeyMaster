"""=============================================================================

  Decorator that records a state processing an event.

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
import inspect
import sys
from statemachine.signals import Signals

RECORDING = "pytest" in sys.modules

def get_or_create_recording(self):
    re1 = getattr(self, '_recording', None)
    if re1 is None:
        re1 = list()
        self._recording = re1
    return re1

def log_during_test(self, text):
    if RECORDING:
        re1 = get_or_create_recording(self)
        re1.append(('L', text))

def record_during_test(f):
    def wrapper_7vEabWWrfTQSyvsXfXSRUHTV(*args, **kwargs):
        event = args[1]
        if event != Signals.GET_SUPER_STATE:
            self = args[0]
            name = f.__name__
            re1 = get_or_create_recording(self)
            current_state_name = self._state.__func__.__name__
            if current_state_name == 'wrapper_7vEabWWrfTQSyvsXfXSRUHTV':
                cv1 = inspect.getclosurevars(self._state.__func__)
                nl1 = cv1.nonlocals
                f1 = nl1.get('f', None)
                current_state_name = f1.__name__
            re1.append(('E', current_state_name, name, event))
            # rmv lo1 = getattr(self, '_logger', None)
            # rmv if lo1 is not None:
            # rmv     #lo1.info('{:<25s}- {:<25s}- {}'.format(current_state_name, name, str(event)))
            # rmv     lo1.info('e1.append(("{}", "{}", {}))'.format(current_state_name, name, str(event)))
        rv = f(*args, **kwargs)
        return rv
    if RECORDING:
        return wrapper_7vEabWWrfTQSyvsXfXSRUHTV
    return f

