"""=============================================================================

  StateMachine for Basic Power Control.

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
from rfidkm.locktypes.BasicPowerControl.BasicPowerControlStateMachine import BasicPowerControlStateMachine

def create_controller_state_machine(controller, config):
    rv1 = BasicPowerControlStateMachine()
    rv1.initialize_machine()
    return rv1
