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
import sys
from statemachine.signals import Signals

RECORDING = "pytest" in sys.modules

def record_during_test(f):
    def wrapper(*args, **kwargs):
        event = args[1]
        if event != Signals.GET_SUPER_STATE:
            self = args[0]
            name = f.__name__
            re1 = getattr(self, '_recording', None)
            if re1 is None:
                re1 = list()
                self._recording = re1
            s1 = self._state.__func__.__name__
            re1.append((name, args[1], s1))
            lo1 = getattr(self, '_logger', None)
            if lo1 is not None:
                lo1.info('{:<25s}- {}'.format(name, event, s1))
        rv = f(*args, **kwargs)
        return rv
    if RECORDING:
        return wrapper
    return f

