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
    TEST_IDLE = auto()
    TEST_1 = auto()
    TEST_2 = auto()
    TEST_3 = auto()
    TEST_4 = auto()
    TEST_5 = auto()
    TEST_TO_TOP = auto()
    TEST_TO_SELF = auto()
    TEST_TO_SIBLING = auto()
    TEST_TO_COUSIN = auto()
    TEST_TO_PARENT = auto()
    TEST_TO_CHILD = auto()
    TEST_TO_GRANDPARENT = auto()
    TEST_TO_GRANDCHILD = auto()
    TEST_TO_DISTANT = auto()
    TEST_TO_FINAL = auto()
    LAST = auto()

create_state_machine_events(LocalTestSignals, __name__)

def test_events_and_signals():
    assert Signals.ENTER_STATE.value == EVENT_ENTER_STATE.signal
    assert Signals.ENTER_STATE == EVENT_ENTER_STATE

class AllTransitionsMachine(StateMachine):
    def _after_init(self):
        super()._after_init()
        self._recording = list()
    def _get_initial_state(self):
        return self.s1
    def _record(self, name, event):
        s1 = self._state.__func__.__name__
        if event != Signals.GET_SUPER_STATE:
            self._recording.append((name, event, s1))
            logger.info('{:<12s}- {}'.format(name, event, s1))
    def s1(self, event):
        self._record('s1', event)
        if event == Signals.INITIALIZE_STATE:
            self._initial_transition(self.s11)
            return None
        if event == LocalTestSignals.TEST_TO_SELF:
            self._transition(self.s1)
            return None
        if event == LocalTestSignals.TEST_TO_SIBLING:
            self._transition(self.s2)
            return None
        return self._top_state
    def s11(self, event):
        self._record('s11', event)
        if event == LocalTestSignals.TEST_TO_COUSIN:
            self._transition(self.s21)
            return None
        if event == LocalTestSignals.TEST_TO_PARENT:
            self._transition(self.s1)
            return None
        if event == LocalTestSignals.TEST_TO_CHILD:
            self._transition(self.s111)
            return None
        return self.s1
    def s111(self, event):
        self._record('s111', event)
        if event == LocalTestSignals.TEST_TO_SELF:
            self._transition(self.s111)
            return None
        if event == LocalTestSignals.TEST_TO_GRANDPARENT:
            self._transition(self.s1)
            return None
        return self.s11
    def s2(self, event):
        self._record('s2', event)
        if event == LocalTestSignals.TEST_TO_SELF:
            self._transition(self.s2)
            return None
        if event == LocalTestSignals.TEST_TO_SIBLING:
            self._transition(self.s3)
            return None
        if event == LocalTestSignals.TEST_TO_CHILD:
            self._transition(self.s21)
            return None
        if event == LocalTestSignals.TEST_TO_GRANDCHILD:
            self._transition(self.s211)
            return None
        return self._top_state
    def s21(self, event):
        self._record('s21', event)
        if event == LocalTestSignals.TEST_TO_COUSIN:
            self._transition(self.s31)
            return None
        if event == LocalTestSignals.TEST_TO_PARENT:
            self._transition(self.s2)
            return None
        if event == LocalTestSignals.TEST_TO_CHILD:
            self._transition(self.s211)
            return None
        return self.s2
    def s211(self, event):
        self._record('s211', event)
        if event == LocalTestSignals.TEST_TO_SELF:
            self._transition(self.s211)
            return None
        if event == LocalTestSignals.TEST_TO_GRANDPARENT:
            self._transition(self.s2)
            return None
        if event == LocalTestSignals.TEST_TO_DISTANT:
            self._transition(self.s4)
            return None
        return self.s21
    def s3(self, event):
        self._record('s3', event)
        if event == LocalTestSignals.TEST_TO_SELF:
            self._transition(self.s3)
            return None
        if event == LocalTestSignals.TEST_TO_SIBLING:
            self._transition(self.s1)
            return None
        if event == LocalTestSignals.TEST_TO_COUSIN:
            if self._is_in(self.s31):
                self._transition(self.s11)
                return None
        if event == LocalTestSignals.TEST_TO_PARENT:
            if self._is_in(self.s31):
                self._transition(self.s3)
                return None
        if event == LocalTestSignals.TEST_TO_CHILD:
            self._transition(self.s31)
            return None
        if event == LocalTestSignals.TEST_TO_GRANDCHILD:
            self._transition(self.s311)
            return None
        if event == LocalTestSignals.TEST_TO_FINAL:
            self._transition(self._final_state)
            return None
        return self._top_state
    def s31(self, event):
        self._record('s31', event)
        return self.s3
    def s311(self, event):
        self._record('s311', event)
        return self.s31
    def s4(self, event):
        self._record('s4', event)
        if event == Signals.INITIALIZE_STATE:
            self._initial_transition(self.s41)
            return None
        if event == LocalTestSignals.TEST_1:
            self._transition(self.s4)
            return None
        return self._top_state
    def s41(self, event):
        self._record('s41', event)
        if event == Signals.INITIALIZE_STATE:
            self._initial_transition(self.s411)
            return None
        if event == LocalTestSignals.TEST_2:
            self._transition(self.s4)
            return None
        if event == LocalTestSignals.TEST_5:
            self._transition(self.s41)
            return None
        return self.s4
    def s411(self, event):
        self._record('s411', event)
        if event == Signals.INITIALIZE_STATE:
            self._initial_transition(self.s4111)
            return None
        if event == LocalTestSignals.TEST_3:
            self._transition(self.s4)
            return None
        return self.s41
    def s4111(self, event):
        self._record('s4111', event)
        if event == LocalTestSignals.TEST_4:
            self._transition(self.s4)
            return None
        if event == LocalTestSignals.TEST_TO_TOP:
            self._transition(self._top_state)
            return None
        if event == LocalTestSignals.TEST_TO_DISTANT:
            self._transition(self.s311)
            return None
        return self.s411

def test_cannot_create_base():
    with pytest.raises(TypeError):
        tm1 = StateMachine()

def test_cannot_target_top():
    tm1 = AllTransitionsMachine()
    with pytest.raises(TopCannotBeTargetError):
        tm1._transition(tm1._top_state)

def test_check_get_super_state():
    tm1 = AllTransitionsMachine()
    assert tm1._get_super_state(tm1.s1) == tm1._top_state
    assert tm1._get_super_state(tm1.s11) == tm1.s1
    assert tm1._get_super_state(tm1.s111) == tm1.s11
    assert tm1._get_super_state(tm1.s2) == tm1._top_state
    assert tm1._get_super_state(tm1.s21) == tm1.s2
    assert tm1._get_super_state(tm1.s211) == tm1.s21
    assert tm1._get_super_state(tm1.s3) == tm1._top_state
    assert tm1._get_super_state(tm1.s31) == tm1.s3
    assert tm1._get_super_state(tm1.s311) == tm1.s31
    assert tm1._get_super_state(tm1.s4) == tm1._top_state
    assert tm1._get_super_state(tm1.s41) == tm1.s4
    assert tm1._get_super_state(tm1.s411) == tm1.s41
    assert tm1._get_super_state(tm1.s4111) == tm1.s411

def test_all_transitions(caplog):
    caplog.set_level(logging.INFO)
    e1 = list()
    tm1 = AllTransitionsMachine()

    tm1.initialize_machine()
    assert tm1.process(EVENT_TEST_TO_SELF)
    assert tm1.process(EVENT_TEST_TO_SIBLING)
    assert tm1.process(EVENT_TEST_TO_SELF)
    assert tm1.process(EVENT_TEST_TO_SIBLING)
    assert tm1.process(EVENT_TEST_TO_SELF)
    assert tm1.process(EVENT_TEST_TO_SIBLING)
    assert tm1.process(EVENT_TEST_TO_PARENT)
    assert tm1.process(EVENT_TEST_TO_COUSIN)
    assert tm1.process(EVENT_TEST_TO_PARENT)
    assert tm1.process(EVENT_TEST_TO_CHILD)
    assert tm1.process(EVENT_TEST_TO_COUSIN)
    assert tm1.process(EVENT_TEST_TO_PARENT)
    assert tm1.process(EVENT_TEST_TO_CHILD)
    assert tm1.process(EVENT_TEST_TO_COUSIN)
    assert tm1.process(EVENT_TEST_TO_CHILD)
    assert not tm1.process(EVENT_TEST_IDLE)
    assert tm1.process(EVENT_TEST_TO_SELF)
    assert tm1.process(EVENT_TEST_TO_GRANDPARENT)
    assert tm1.process(EVENT_TEST_TO_COUSIN)
    assert tm1.process(EVENT_TEST_TO_CHILD)
    assert not tm1.process(EVENT_TEST_IDLE)
    assert tm1.process(EVENT_TEST_TO_COUSIN)
    assert tm1.process(EVENT_TEST_TO_PARENT)
    assert tm1.process(EVENT_TEST_TO_GRANDCHILD)
    assert tm1.process(EVENT_TEST_TO_SIBLING)
    assert tm1.process(EVENT_TEST_TO_SIBLING)
    assert tm1.process(EVENT_TEST_TO_GRANDCHILD)
    assert tm1.process(EVENT_TEST_TO_DISTANT)
    assert tm1.process(EVENT_TEST_1)
    assert tm1.process(EVENT_TEST_2)
    assert tm1.process(EVENT_TEST_3)
    assert tm1.process(EVENT_TEST_4)
    assert tm1.process(EVENT_TEST_5)
    assert not tm1.process(EVENT_TEST_TO_FINAL)
    with pytest.raises(TopCannotBeTargetError):
        tm1.process(EVENT_TEST_TO_TOP)
    assert tm1.process(EVENT_TEST_TO_DISTANT)
    assert tm1.process(EVENT_TEST_TO_FINAL)
    for i1 in range(LocalTestSignals.FIRST, LocalTestSignals.LAST+1):
        assert not tm1.process(i1)

    tm2 = [(e[0], str(e[1])) for e in tm1._recording]
    logger.info(tm2)
    #logger.info(e1)
    #assert e1 == tm2
