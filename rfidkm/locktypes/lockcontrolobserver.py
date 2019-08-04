"""=============================================================================

  Controllers are required to implement this interface so locktype state
  machines can issue commands.

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
from rfidkm.statemachine import log_during_test

class LockControlObserver():
    def __init__(self, subject):
        self._subject = subject
    def close_relay(self):
        self._subject.relay_is_closed = True
    def open_relay(self):
        self._subject.relay_is_closed = False
    def start_timeout_timer(self, seconds):
        pass
    def stop_timeout_timer(self):
        pass
    def log(lvl, msg, *args, **kwargs):
        pass

class LockControlObserverForTesting(LockControlObserver):
    def close_relay(self):
        super().close_relay()
        log_during_test(self._subject, 'close the relay')
    def open_relay(self):
        super().open_relay()
        log_during_test(self._subject, 'open the relay')
    def start_timeout_timer(self, seconds):
        super().start_timeout_timer(seconds)
        log_during_test(self._subject, 'post a timeout in {} seconds'.format(seconds))
    def stop_timeout_timer(self):
        super().stop_timeout_timer()
        log_during_test(self._subject, 'cancel the timeout request')
    def log(lvl, msg, *args, **kwargs):
        # fix: log_during_test
        pass
