"""=============================================================================

  Provide a factory for creating state machines for lock types.  Loadable
  Drivers are found by searching through the drivers directory.  The same
  could be done here.  But, there is only one state machine so it is not worth
  the additional code (risk).  At least not until there is a second state
  machine.

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
from .lockcontrolobserver import LockControlObserver

def create_state_machine(class_name, controller, config):
    pass
