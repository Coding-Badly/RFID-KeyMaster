"""=============================================================================

  Tests for the Basic Power Control State Machine.

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
import logging
from locktypes.BasicPowerControl import create_controller_state_machine
from locktypes.BasicPowerControl.BasicPowerControlStateMachine import PowerControlSignals
from drivers.signals import KeyMasterSignals, Signals, UserAuthorizedEvent, UserDeniedEvent
from statemachine import StateMachineEvent, log_during_test

logger = logging.getLogger(__name__)

# pytest tests/test_BasicPowerControl.py

def log_recording(recording):
    for record in recording:
        if record[0] == 'L':
            logger.info('e1.append(("L", "{}"))'.format(record[1]))
        elif record[0] == 'E':
            logger.info('e1.append(("E", "{}", "{}", {}))'.format(record[1], record[2], record[3]))
        else:
            logger.info('unknown')

def create_to_manual_override(order):
    e1 = list()
    tm1 = create_controller_state_machine(None, None)
    e1.append(('E', "initial_hardware_check", "initial_hardware_check", Signals.ENTER_STATE))
    e1.append(('E', "initial_hardware_check", "initial_hardware_check", Signals.INITIALIZE_STATE))
    assert e1 == tm1._recording
    if order == 1:
        tm1.process_relay_closed(False)
        tm1.process_current_flowing(True)
    else:
        tm1.process_current_flowing(True)
        tm1.process_relay_closed(False)
    e1.append(('E', "initial_hardware_check", "initial_hardware_check", PowerControlSignals.OPEN_FLOW))
    e1.append(('E', "initial_hardware_check", "initial_hardware_check", Signals.EXIT_STATE))
    e1.append(('E', "_top_state", "authorized_jump", Signals.ENTER_STATE))
    e1.append(('E', "authorized_jump", "wait_for_swipe", Signals.ENTER_STATE))
    e1.append(('E', "wait_for_swipe", "wait_for_swipe", Signals.INITIALIZE_STATE))
    e1.append(('E', "manual_override", "manual_override", Signals.ENTER_STATE))
    e1.append(('E', "manual_override", "manual_override", Signals.INITIALIZE_STATE))
    assert e1 == tm1._recording
    return (e1, tm1)

def test_manual_override_from_startup(caplog):
    caplog.set_level(logging.INFO)
    for order in range(1,3):
        e1, tm1 = create_to_manual_override(order)
        log_recording(tm1._recording)
        logger.info('----------')

def create_to_boring(order):
    e1 = list()
    tm1 = create_controller_state_machine(None, None)
    e1.append(('E', "initial_hardware_check", "initial_hardware_check", Signals.ENTER_STATE))
    e1.append(('E', "initial_hardware_check", "initial_hardware_check", Signals.INITIALIZE_STATE))
    assert e1 == tm1._recording
    if order == 1:
        tm1.process_relay_closed(False)
        tm1.process_current_flowing(False)
    else:
        tm1.process_current_flowing(False)
        tm1.process_relay_closed(False)
    e1.append(('E', "initial_hardware_check", "initial_hardware_check", PowerControlSignals.OPEN_NONE))
    e1.append(('E', "initial_hardware_check", "initial_hardware_check", Signals.EXIT_STATE))
    e1.append(('E', "_top_state", "authorized_jump", Signals.ENTER_STATE))
    e1.append(('E', "authorized_jump", "wait_for_swipe", Signals.ENTER_STATE))
    e1.append(('E', "wait_for_swipe", "wait_for_swipe", Signals.INITIALIZE_STATE))
    assert e1 == tm1._recording
    return (e1, tm1)

def test_boring_from_startup(caplog):
    caplog.set_level(logging.INFO)
    for order in range(1,3):
        e1, tm1 = create_to_boring(order)
        log_recording(tm1._recording)
        logger.info('----------')

def test_relay_left_closed_from_startup(caplog):
    caplog.set_level(logging.INFO)
    e1 = list()
    tm1 = create_controller_state_machine(None, None)
    e1.append(('E', "initial_hardware_check", "initial_hardware_check", Signals.ENTER_STATE))
    e1.append(('E', "initial_hardware_check", "initial_hardware_check", Signals.INITIALIZE_STATE))
    assert e1 == tm1._recording
    tm1.process_relay_closed(True)
    tm1.process_current_flowing(False)
    e1.append(('E', "initial_hardware_check", "initial_hardware_check", PowerControlSignals.CLOSED_NONE))
    e1.append(('L', 'open the relay'))
    e1.append(('E', "initial_hardware_check", "initial_hardware_check", Signals.EXIT_STATE))
    e1.append(('E', "_top_state", "authorized_jump", Signals.ENTER_STATE))
    e1.append(('E', "authorized_jump", "wait_for_swipe", Signals.ENTER_STATE))
    e1.append(('E', "wait_for_swipe", "wait_for_swipe", Signals.INITIALIZE_STATE))
    log_recording(tm1._recording)
    assert e1 == tm1._recording
    logger.info('----------')
    # Ensure setting current flowing and relay closed is orthogonal
    tm1 = create_controller_state_machine(None, None)
    tm1.process_current_flowing(False)
    tm1.process_relay_closed(True)
    log_recording(tm1._recording)
    assert e1 == tm1._recording

def create_to_ghost_active(order):
    e1 = list()
    tm1 = create_controller_state_machine(None, None)
    e1.append(('E', "initial_hardware_check", "initial_hardware_check", Signals.ENTER_STATE))
    e1.append(('E', "initial_hardware_check", "initial_hardware_check", Signals.INITIALIZE_STATE))
    assert e1 == tm1._recording
    if order == 1:
        tm1.process_relay_closed(True)
        tm1.process_current_flowing(True)
    else:
        tm1.process_current_flowing(True)
        tm1.process_relay_closed(True)
    e1.append(('E', "initial_hardware_check", "initial_hardware_check", PowerControlSignals.CLOSED_FLOW))
    e1.append(('E', "initial_hardware_check", "initial_hardware_check", Signals.EXIT_STATE))
    e1.append(('E', "_top_state", "authorized_jump", Signals.ENTER_STATE))
    e1.append(('E', "authorized_jump", "ghost", Signals.ENTER_STATE))
    e1.append(('E', "ghost", "ghost_active", Signals.ENTER_STATE))
    e1.append(('E', "ghost_active", "ghost_active", Signals.INITIALIZE_STATE))
    assert e1 == tm1._recording
    return (e1, tm1)

def test_machine_running_from_startup(caplog):
    caplog.set_level(logging.INFO)
    for order in range(1,3):
        e1, tm1 = create_to_ghost_active(order)
        log_recording(tm1._recording)
        logger.info('----------')

def do_ghost_idle_exit(trigger):
    e1, tm1 = create_to_ghost_active(1)
    tm1.process_current_flowing(False)
    e1.append(("E", "ghost_active", "ghost_active", PowerControlSignals.CLOSED_NONE))
    e1.append(("E", "ghost_active", "ghost_active", Signals.EXIT_STATE))
    e1.append(("E", "ghost", "ghost_idle", Signals.ENTER_STATE))
    e1.append(("L", "post a timeout in 5 seconds"))
    e1.append(("E", "ghost_idle", "ghost_idle", Signals.INITIALIZE_STATE))
    tm1.process(trigger)
    e1.append(("E", "ghost_idle", "ghost_idle", trigger))
    e1.append(("L", "open the relay"))
    e1.append(("E", "ghost_idle", "ghost_idle", Signals.EXIT_STATE))
    e1.append(("L", "cancel the timeout request"))
    e1.append(("E", "ghost", "ghost", Signals.EXIT_STATE))
    e1.append(("E", "authorized_jump", "wait_for_swipe", Signals.ENTER_STATE))
    e1.append(("E", "wait_for_swipe", "wait_for_swipe", Signals.INITIALIZE_STATE))
    log_recording(tm1._recording)
    assert e1 == tm1._recording

def test_ghost_idle_timeout_001(caplog):
    caplog.set_level(logging.INFO)
    do_ghost_idle_exit(Signals.TIMEOUT)

def test_ghost_idle_denied(caplog):
    caplog.set_level(logging.INFO)
    do_ghost_idle_exit(KeyMasterSignals.USER_DENIED)

def test_ghost_idle_timeout_002(caplog):
    caplog.set_level(logging.INFO)
    e1, tm1 = create_to_ghost_active(1)
    tm1.process_current_flowing(False)
    e1.append(("E", "ghost_active", "ghost_active", PowerControlSignals.CLOSED_NONE))
    e1.append(("E", "ghost_active", "ghost_active", Signals.EXIT_STATE))
    e1.append(("E", "ghost", "ghost_idle", Signals.ENTER_STATE))
    e1.append(("L", "post a timeout in 5 seconds"))
    e1.append(("E", "ghost_idle", "ghost_idle", Signals.INITIALIZE_STATE))
    tm1.process_current_flowing(True)
    e1.append(("E", "ghost_idle", "ghost_idle", PowerControlSignals.CLOSED_FLOW))
    e1.append(("E", "ghost_idle", "ghost_idle", Signals.EXIT_STATE))
    e1.append(("L", "cancel the timeout request"))
    e1.append(("E", "ghost", "ghost_active", Signals.ENTER_STATE))
    e1.append(("E", "ghost_active", "ghost_active", Signals.INITIALIZE_STATE))
    tm1.process_current_flowing(False)
    e1.append(("E", "ghost_active", "ghost_active", PowerControlSignals.CLOSED_NONE))
    e1.append(("E", "ghost_active", "ghost_active", Signals.EXIT_STATE))
    e1.append(("E", "ghost", "ghost_idle", Signals.ENTER_STATE))
    e1.append(("L", "post a timeout in 5 seconds"))
    e1.append(("E", "ghost_idle", "ghost_idle", Signals.INITIALIZE_STATE))
    tm1.process(Signals.TIMEOUT)
    e1.append(("E", "ghost_idle", "ghost_idle", Signals.TIMEOUT))
    e1.append(("L", "open the relay"))
    e1.append(("E", "ghost_idle", "ghost_idle", Signals.EXIT_STATE))
    e1.append(("L", "cancel the timeout request"))
    e1.append(("E", "ghost", "ghost", Signals.EXIT_STATE))
    e1.append(("E", "authorized_jump", "wait_for_swipe", Signals.ENTER_STATE))
    e1.append(("E", "wait_for_swipe", "wait_for_swipe", Signals.INITIALIZE_STATE))
    log_recording(tm1._recording)
    assert e1 == tm1._recording

def test_manual_override(caplog):
    caplog.set_level(logging.INFO)
    e1, tm1 = create_to_manual_override(1)
    tm1.process_current_flowing(False)
    e1.append(("E", "manual_override", "manual_override", PowerControlSignals.OPEN_NONE))
    e1.append(("E", "manual_override", "manual_override", Signals.EXIT_STATE))
    e1.append(("E", "wait_for_swipe", "wait_for_swipe", Signals.INITIALIZE_STATE))
    tm1.process_current_flowing(True)
    e1.append(("E", "wait_for_swipe", "wait_for_swipe", PowerControlSignals.OPEN_FLOW))
    e1.append(("E", "wait_for_swipe", "manual_override", Signals.ENTER_STATE))
    e1.append(("E", "manual_override", "manual_override", Signals.INITIALIZE_STATE))
    log_recording(tm1._recording)
    assert e1 == tm1._recording

def test_simple_authorized(caplog):
    caplog.set_level(logging.INFO)
    e1, tm1 = create_to_boring(1)
    tm1.process(UserAuthorizedEvent('0006276739'))  # red tag
    e1.append(("E", "wait_for_swipe", "wait_for_swipe", KeyMasterSignals.USER_AUTHORIZED))
    e1.append(("E", "wait_for_swipe", "authorized_jump", KeyMasterSignals.USER_AUTHORIZED))
    e1.append(("E", "wait_for_swipe", "wait_for_swipe", Signals.EXIT_STATE))
    e1.append(("E", "authorized_jump", "closed", Signals.ENTER_STATE))
    e1.append(("L", "close the relay"))
    e1.append(("E", "closed", "keep_closed", Signals.ENTER_STATE))
    e1.append(("E", "keep_closed", "authorized", Signals.ENTER_STATE))
    e1.append(("E", "authorized", "authorized", Signals.INITIALIZE_STATE))
    e1.append(("E", "authorized_idle", "authorized_idle", Signals.ENTER_STATE))
    e1.append(("L", "post a timeout in 300 seconds"))
    e1.append(("E", "authorized_idle", "authorized_idle", Signals.INITIALIZE_STATE))
    tm1.process_current_flowing(True)
    e1.append(("E", "authorized_idle", "authorized_idle", PowerControlSignals.CLOSED_FLOW))
    e1.append(("E", "authorized_idle", "authorized_idle", Signals.EXIT_STATE))
    e1.append(("L", "cancel the timeout request"))
    e1.append(("E", "authorized", "authorized_active", Signals.ENTER_STATE))
    e1.append(("E", "authorized_active", "authorized_active", Signals.INITIALIZE_STATE))
    tm1.process_current_flowing(False)
    e1.append(("E", "authorized_active", "authorized_active", PowerControlSignals.CLOSED_NONE))
    e1.append(("E", "authorized_active", "authorized_active", Signals.EXIT_STATE))
    e1.append(("E", "authorized", "authorized_idle", Signals.ENTER_STATE))
    e1.append(("L", "post a timeout in 300 seconds"))
    e1.append(("E", "authorized_idle", "authorized_idle", Signals.INITIALIZE_STATE))
    log_recording(tm1._recording)
    assert e1 == tm1._recording

def test_simple_denied(caplog):
    caplog.set_level(logging.INFO)
    e1, tm1 = create_to_boring(1)
    tm1.process(UserDeniedEvent('0002864796'))  # blue tag
    e1.append(("E", "wait_for_swipe", "wait_for_swipe", KeyMasterSignals.USER_DENIED))
    e1.append(("E", "wait_for_swipe", "authorized_jump", KeyMasterSignals.USER_DENIED))
    log_recording(tm1._recording)
    assert e1 == tm1._recording

def test_authorized_from_manual_override(caplog):
    caplog.set_level(logging.INFO)
    e1, tm1 = create_to_manual_override(1)
    tm1.process(UserAuthorizedEvent('0006276739'))  # red tag
    e1.append(("E", "manual_override", "manual_override", KeyMasterSignals.USER_AUTHORIZED))
    e1.append(("E", "manual_override", "wait_for_swipe", KeyMasterSignals.USER_AUTHORIZED))
    e1.append(("E", "manual_override", "authorized_jump", KeyMasterSignals.USER_AUTHORIZED))
    e1.append(("E", "manual_override", "manual_override", Signals.EXIT_STATE))
    e1.append(("E", "wait_for_swipe", "wait_for_swipe", Signals.EXIT_STATE))
    e1.append(("E", "authorized_jump", "closed", Signals.ENTER_STATE))
    e1.append(("L", "close the relay"))
    e1.append(("E", "closed", "keep_closed", Signals.ENTER_STATE))
    e1.append(("E", "keep_closed", "authorized", Signals.ENTER_STATE))
    e1.append(("E", "authorized", "authorized", Signals.INITIALIZE_STATE))
    e1.append(("E", "authorized_active", "authorized_active", Signals.ENTER_STATE))
    e1.append(("E", "authorized_active", "authorized_active", Signals.INITIALIZE_STATE))
    tm1.process_current_flowing(False)
    e1.append(("E", "authorized_active", "authorized_active", PowerControlSignals.CLOSED_NONE))
    e1.append(("E", "authorized_active", "authorized_active", Signals.EXIT_STATE))
    e1.append(("E", "authorized", "authorized_idle", Signals.ENTER_STATE))
    e1.append(("L", "post a timeout in 300 seconds"))
    e1.append(("E", "authorized_idle", "authorized_idle", Signals.INITIALIZE_STATE))
    #log_during_test(tm1, '----------')
    tm1.process_current_flowing(True)
    e1.append(("E", "authorized_idle", "authorized_idle", PowerControlSignals.CLOSED_FLOW))
    e1.append(("E", "authorized_idle", "authorized_idle", Signals.EXIT_STATE))
    e1.append(("L", "cancel the timeout request"))
    e1.append(("E", "authorized", "authorized_active", Signals.ENTER_STATE))
    e1.append(("E", "authorized_active", "authorized_active", Signals.INITIALIZE_STATE))
    log_recording(tm1._recording)
    assert e1 == tm1._recording

def test_ghost_active_authorized(caplog):
    caplog.set_level(logging.INFO)
    e1, tm1 = create_to_ghost_active(1)
    tm1.process(UserAuthorizedEvent('0006276739'))  # red tag
    e1.append(("E", "ghost_active", "ghost_active", KeyMasterSignals.USER_AUTHORIZED))
    e1.append(("E", "ghost_active", "ghost", KeyMasterSignals.USER_AUTHORIZED))
    e1.append(("E", "ghost_active", "authorized_jump", KeyMasterSignals.USER_AUTHORIZED))
    e1.append(("E", "ghost_active", "ghost_active", Signals.EXIT_STATE))
    e1.append(("E", "ghost", "ghost", Signals.EXIT_STATE))
    e1.append(("E", "authorized_jump", "closed", Signals.ENTER_STATE))
    e1.append(("L", "close the relay"))
    e1.append(("E", "closed", "keep_closed", Signals.ENTER_STATE))
    e1.append(("E", "keep_closed", "authorized", Signals.ENTER_STATE))
    e1.append(("E", "authorized", "authorized", Signals.INITIALIZE_STATE))
    e1.append(("E", "authorized_active", "authorized_active", Signals.ENTER_STATE))
    e1.append(("E", "authorized_active", "authorized_active", Signals.INITIALIZE_STATE))
    log_recording(tm1._recording)
    assert e1 == tm1._recording

def test_ghost_idle_authorized(caplog):
    caplog.set_level(logging.INFO)
    e1, tm1 = create_to_ghost_active(1)
    tm1.process_current_flowing(False)
    e1.append(("E", "ghost_active", "ghost_active", PowerControlSignals.CLOSED_NONE))
    e1.append(("E", "ghost_active", "ghost_active", Signals.EXIT_STATE))
    e1.append(("E", "ghost", "ghost_idle", Signals.ENTER_STATE))
    e1.append(("L", "post a timeout in 5 seconds"))
    e1.append(("E", "ghost_idle", "ghost_idle", Signals.INITIALIZE_STATE))
    tm1.process(UserAuthorizedEvent('0006276739'))  # red tag
    e1.append(("E", "ghost_idle", "ghost_idle", KeyMasterSignals.USER_AUTHORIZED))
    e1.append(("E", "ghost_idle", "ghost", KeyMasterSignals.USER_AUTHORIZED))
    e1.append(("E", "ghost_idle", "authorized_jump", KeyMasterSignals.USER_AUTHORIZED))
    e1.append(("E", "ghost_idle", "ghost_idle", Signals.EXIT_STATE))
    e1.append(("L", "cancel the timeout request"))
    e1.append(("E", "ghost", "ghost", Signals.EXIT_STATE))
    e1.append(("E", "authorized_jump", "closed", Signals.ENTER_STATE))
    e1.append(("L", "close the relay"))
    e1.append(("E", "closed", "keep_closed", Signals.ENTER_STATE))
    e1.append(("E", "keep_closed", "authorized", Signals.ENTER_STATE))
    e1.append(("E", "authorized", "authorized", Signals.INITIALIZE_STATE))
    e1.append(("E", "authorized_idle", "authorized_idle", Signals.ENTER_STATE))
    e1.append(("L", "post a timeout in 300 seconds"))
    e1.append(("E", "authorized_idle", "authorized_idle", Signals.INITIALIZE_STATE))
    log_recording(tm1._recording)
    assert e1 == tm1._recording

