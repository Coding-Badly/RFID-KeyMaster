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
import enum
import logging
from drivers.signals import Signals, KeyMasterSignals, UserFinishedEvent
from statemachine import log_during_test, record_during_test, StateMachine, StateMachineEvent

# rmv logger = logging.getLogger(__name__)

class PowerControlSignals(enum.IntEnum):
    FIRST = KeyMasterSignals.LAST
    OPEN_NONE = enum.auto()
    OPEN_FLOW = enum.auto()
    CLOSED_NONE = enum.auto()
    CLOSED_FLOW = enum.auto()

# https://drive.google.com/drive/u/2/folders/1tiE0BajeXZB4ZV3zA4-h33tj5u9IZf24
# https://en.wikipedia.org/wiki/Observer_pattern

class PowerControlObserver():
    def __init__(self, subject):
        self._subject = subject
    def close_relay(self):
        log_during_test(self._subject, 'close the relay')
        self._subject.relay_is_closed = True
    def open_relay(self):
        log_during_test(self._subject, 'open the relay')
        self._subject.relay_is_closed = False
    def start_timeout_timer(self, seconds):
        log_during_test(self._subject, 'post a timeout in {} seconds'.format(seconds))
    def stop_timeout_timer(self):
        log_during_test(self._subject, 'cancel the timeout request')
    def log(lvl, msg, *args, **kwargs):
        # fix: log_during_test
        pass

class BasicPowerControlStateMachine(StateMachine):
    def _after_init(self):
        super()._after_init()
        self.current_is_flowing = None
        self.relay_is_closed = None
        self._observer = PowerControlObserver(self)
        self._active_member_id = None
        self._pending_member_id = None
    def _get_initial_state(self):
        return self.initial_hardware_check
    def _close_relay(self):
        # keep? rmv? self.relay_is_closed = True
        self._observer.close_relay()
    def _open_relay(self):
        # keep? rmv? self.relay_is_closed = False
        self._observer.open_relay()
    def _generate_relay_current(self):
        if (self.current_is_flowing is not None) \
                and (self.relay_is_closed is not None):
            if self.relay_is_closed:
                if self.current_is_flowing:
                    self.process(PowerControlSignals.CLOSED_FLOW)
                else:
                    self.process(PowerControlSignals.CLOSED_NONE)
            else:
                if self.current_is_flowing:
                    self.process(PowerControlSignals.OPEN_FLOW)
                else:
                    self.process(PowerControlSignals.OPEN_NONE)
    def process_current_flowing(self, current_flowing):
        self.current_is_flowing = current_flowing
        self._generate_relay_current()
    def process_relay_closed(self, relay_closed):
        self.relay_is_closed = relay_closed
        self._generate_relay_current()
    @record_during_test
    def initial_hardware_check(self, event):
        if event == PowerControlSignals.OPEN_FLOW:
            self._transition(self.wait_for_swipe)
            return None
        if event == PowerControlSignals.OPEN_NONE:
            self._transition(self.wait_for_swipe)
            return None
        if event == PowerControlSignals.CLOSED_NONE:
            self._open_relay()
            self._transition(self.wait_for_swipe)
            return None
        if event == PowerControlSignals.CLOSED_FLOW:
            self._transition(self.ghost_active)
            return None
        return self._top_state
    @record_during_test
    def authorized_jump(self, event):
        if event == KeyMasterSignals.USER_AUTHORIZED:
            if event.id != self._active_member_id:
                self._pending_member_id = event.id
                self._transition(self.authorized)
                return None
            else:
                self._post_signal(UserFinishedEvent(event.id))
                return None
        return self._top_state
    @record_during_test
    def wait_for_swipe(self, event):
        if event == Signals.INITIALIZE_STATE:
            if self.current_is_flowing:
                self._initial_transition(self.manual_override)
                return None
        if event == PowerControlSignals.OPEN_FLOW:
            self._transition(self.manual_override)
            return None
        return self.authorized_jump
    @record_during_test
    def manual_override(self, event):
        if event == Signals.ENTER_STATE:
            self._observer.log(logging.WARNING, 'Power to the tool has been manually overridden (relay is open; current is flowing).')
            return None
        if event == PowerControlSignals.OPEN_NONE:
            self._transition(self.wait_for_swipe)
            return None
        if event == Signals.EXIT_STATE:
            self._observer.log(logging.WARNING, 'Manual override has ended (relay is open; current is not flowing).')
            return None
        return self.wait_for_swipe
    @record_during_test
    def ghost(self, event):
        return self.authorized_jump
    @record_during_test
    def ghost_active(self, event):
        if event == PowerControlSignals.CLOSED_NONE:
            self._transition(self.ghost_idle)
            return None
        return self.ghost
    @record_during_test
    def ghost_idle(self, event):
        if event == Signals.ENTER_STATE:
            self._observer.start_timeout_timer(5)
            return None
        if event == PowerControlSignals.CLOSED_FLOW:
            self._transition(self.ghost_active)
            return None
        if (event == Signals.TIMEOUT) \
                or (event == KeyMasterSignals.USER_DENIED):
            self._open_relay()
            self._transition(self.wait_for_swipe)
            return None
        if event == Signals.EXIT_STATE:
            self._observer.stop_timeout_timer()
            return None
        return self.ghost

    @record_during_test
    def closed(self, event):
        if event == Signals.ENTER_STATE:
            self._close_relay()
            return None
        if event == Signals.EXIT_STATE:
            self._open_relay()
            return None
        return self.authorized_jump
    @record_during_test
    def keep_closed(self, event):
        return self.closed
    @record_during_test
    def authorized(self, event):
        if event == Signals.ENTER_STATE:
            self._active_member_id = self._pending_member_id
            self._pending_member_id = None
            return None
        if event == Signals.INITIALIZE_STATE:
            if self.current_is_flowing:
                self._initial_transition(self.authorized_active)
                return None
            else:
                self._initial_transition(self.authorized_idle)
                return None
        if event == Signals.EXIT_STATE:
            self._active_member_id = None
            self._pending_member_id = None
            return None
        return self.keep_closed
    @record_during_test
    def authorized_idle(self, event):
        if event == Signals.ENTER_STATE:
            self._observer.start_timeout_timer(5*60)
            return None
        if event == PowerControlSignals.CLOSED_FLOW:
            self._transition(self.authorized_active)
            return None
        if (event == Signals.TIMEOUT) \
                or (event == KeyMasterSignals.USER_DENIED):
            # fix: not tested
            self._transition(self.wait_for_swipe)
            return None
        if event == Signals.EXIT_STATE:
            self._observer.stop_timeout_timer()
            return None
        return self.authorized
    @record_during_test
    def authorized_active(self, event):
        if event == PowerControlSignals.CLOSED_NONE:
            self._transition(self.authorized_idle)
            return None
        return self.authorized
    @record_during_test
    def limbo(self, event):
        return self.keep_closed


    @record_during_test
    def rmv_authorized(self, event):
        if event == Signals.ENTER_STATE:
            self._active_member_id = self._pending_member_id
            self._pending_member_id = None
            return None
        if event == Signals.INITIALIZE_STATE:
            if self.current_is_flowing:
                self._initial_transition(self.authorized_active)
            else:
                self._initial_transition(self.authorized_idle)
            return None
        if event == Signals.EXIT_STATE:
            self._active_member_id = None
            return None
        return self.closed
    @record_during_test
    def rmv_authorized_idle(self, event):
        if event == Signals.ENTER_STATE:
            self._observer.start_timeout_timer(5*60)
            return None
        if event == KeyMasterSignals.USER_AUTHORIZED:
            if self._active_member_id == event.id:
                self._transition(self.wait_for_swipe)
            else:
                self._pending_member_id = event.id
                self._transition(self.authorized)
            return None
        if event == Signals.TIMEOUT:
            self._transition(self.wait_for_swipe)
            return None
        if event == PowerControlSignals.CLOSED_FLOW:
            self._transition(self.authorized_active)
            return None
        if event == Signals.EXIT_STATE:
            self._observer.stop_timeout_timer()
            return None
        return self.authorized
    @record_during_test
    def rmv_authorized_active(self, event):
        return self.authorized
