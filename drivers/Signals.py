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

STOP_NOW                    = 'stop_now'
CONTROL_TARGET              = 'control_target'
SWIPE_10                    = 'swipe_10'
FRESH_DATA                  = 'fresh_member_data'
CACHED_DATA                 = 'cached_member_data'
USER_LOGGED_IN              = 'user_logged_in'
USER_LOGGED_OUT             = 'user_logged_out'
USER_LOGIN_FAILED           = 'user_login_failed'
# rmv LOGIN_RFID_NOT_FOUND        = 'login_rfid_not_found'
# rmv LOGIN_PERMISSION_DENIED     = 'login_permission_denied'
# rmv LOGIN_SUCCESS               = 'login_success'
