from enum import IntEnum, auto
import logging
import pytest
from drivers.state_machine import EVENT_ENTER_STATE, TopCannotBeTargetError, StateMachine, create_state_machine_events
from drivers.signals import Signals, KeyMasterSignals

# cls & pytest tests/test_state_machine.py

logger = logging.getLogger(__name__)

class LocalTestSignals(IntEnum):
    __test__ = False
    FIRST = KeyMasterSignals.FIRST
    TEST_1 = auto()
    TEST_2 = auto()
    TEST_3 = auto()
    TEST_4 = auto()
    TEST_5 = auto()
    TEST_TO_TOP = auto()
    TEST_TO_SELF = auto()
    TEST_TO_SIBLING = auto()
    TEST_TO_FINAL = auto()
    LAST = auto()

create_state_machine_events(LocalTestSignals, __name__)

def test_events_and_signals():
    assert Signals.ENTER_STATE.value == EVENT_ENTER_STATE.signal
    assert Signals.ENTER_STATE == EVENT_ENTER_STATE

class OneStateWonder(StateMachine):
    def _after_init(self):
        super()._after_init()
        self.processed = set()
    def _get_initial_state(self):
        return self.one_state
    def one_state(self, event):
        if event == Signals.ENTER_STATE:
            logger.info('one_state:ENTER_STATE')
            self.processed.add(Signals.ENTER_STATE)
            return None
        if event == LocalTestSignals.TEST_1:
            logger.info('one_state:TEST_1')
            self.processed.add(LocalTestSignals.TEST_1)
            self._post_signal(LocalTestSignals.TEST_3)
            return None
        if event == LocalTestSignals.TEST_3:
            logger.info('one_state:TEST_3')
            self.processed.add(LocalTestSignals.TEST_3)
            self._post_signal(LocalTestSignals.TEST_4)
            self._post_signal(LocalTestSignals.TEST_5)
            return None
        if event == LocalTestSignals.TEST_4:
            logger.info('one_state:TEST_4')
            self.processed.add(LocalTestSignals.TEST_4)
            return None
        if event == LocalTestSignals.TEST_5:
            logger.info('one_state:TEST_5')
            self.processed.add(LocalTestSignals.TEST_5)
            return None
        if event == LocalTestSignals.TEST_TO_TOP:
            self._transition(self._top_state)
            return None
        return self._top_state

class TwoStateWonder(StateMachine):
    def _get_initial_state(self):
        return self.state1
    def state1(self, event):
        if event == Signals.INITIALIZE_STATE:
            self._initial_transition(self.state11)
            return None
        if event == Signals.ENTER_STATE:
            logger.info('state1:ENTER_STATE')
            return None
        if event == LocalTestSignals.TEST_1:
            logger.info('state1:TEST_1')
            return None
        return self._top_state
    def state11(self, event):
        if event == Signals.ENTER_STATE:
            logger.info('state11:ENTER_STATE')
            return None
        if event == LocalTestSignals.TEST_2:
            logger.info('state11:TEST_2')
            self._transition(self.state12)
            return None
        if event == LocalTestSignals.TEST_3:
            logger.info('state11:TEST_3')
            self._transition(self.state12)
            return None
        return self.state1
    def state12(self, event):
        if event == Signals.ENTER_STATE:
            logger.info('state12:ENTER_STATE')
            return None
        if event == LocalTestSignals.TEST_2:
            logger.info('state12:TEST_2')
            return None
        return self.state1

class AllTransitionsMachine(StateMachine):
    def _get_initial_state(self):
        return self.state1

    def state1(self, event):
        logger.info('s1: {}'.format(event))
        if event == LocalTestSignals.TEST_TO_SELF:
            self._transition(self.state1)
            return None
        if event == LocalTestSignals.TEST_TO_SIBLING:
            self._transition(self.state2)
            return None
        if event == LocalTestSignals.TEST_TO_FINAL:
            self._transition(self._final_state)
            return None
        return self._top_state
    def state11(self, event):
        return self.state1
    def state12(self, event):
        return self.state1
    def state13(self, event):
        return self.state1

    def state2(self, event):
        logger.info('s2: {}'.format(event))
        if event == LocalTestSignals.TEST_TO_SELF:
            self._transition(self.state2)
            return None
        if event == LocalTestSignals.TEST_TO_SIBLING:
            self._transition(self.state3)
            return None
        if event == LocalTestSignals.TEST_TO_FINAL:
            self._transition(self._final_state)
            return None
        return self._top_state
    def state21(self, event):
        return self.state2
    def state22(self, event):
        return self.state2
    def state23(self, event):
        return self.state2

    def state3(self, event):
        logger.info('s3: {}'.format(event))
        if event == LocalTestSignals.TEST_TO_SELF:
            self._transition(self.state3)
            return None
        if event == LocalTestSignals.TEST_TO_SIBLING:
            self._transition(self.state1)
            return None
        if event == LocalTestSignals.TEST_TO_FINAL:
            self._transition(self._final_state)
            return None
        return self._top_state

def test_cannot_create_base():
    with pytest.raises(TypeError):
        tm1 = StateMachine()

#def test_cannot_target_top():
    tm1 = OneStateWonder()
    with pytest.raises(TopCannotBeTargetError):
        tm1._transition(tm1._top_state)

def test_check_get_super_state():
    tm1 = OneStateWonder()
    assert tm1._get_super_state(tm1.one_state) == tm1._top_state

def test_simple_normal(caplog):
    caplog.set_level(logging.INFO)
    tm1 = OneStateWonder()
    tm1.initialize_machine()
    assert tm1.process(EVENT_TEST_1)
    assert not tm1.process(EVENT_TEST_2)
    assert tm1.processed == set([Signals.ENTER_STATE, 
            LocalTestSignals.TEST_1, 
            LocalTestSignals.TEST_3, 
            LocalTestSignals.TEST_4, 
            LocalTestSignals.TEST_5])
    with pytest.raises(TopCannotBeTargetError):
        tm1.process(EVENT_TEST_TO_TOP)
    tm1 = TwoStateWonder()
    tm1.initialize_machine()
    #assert tm1.process(EVENT_TEST_1)
    #assert tm1.process(EVENT_TEST_2)
    #assert tm1.process(EVENT_TEST_3)

def test_all_transitions(caplog):
    caplog.set_level(logging.INFO)
    tm1 = AllTransitionsMachine()
    tm1.initialize_machine()
    logger.info('--> {}'.format(tm1._state.__func__))
    tm1.process(EVENT_TEST_TO_SIBLING)
    logger.info('--> {}'.format(tm1._state.__func__))
    tm1.process(EVENT_TEST_TO_FINAL)
    logger.info('--> {}'.format(tm1._state.__func__))
