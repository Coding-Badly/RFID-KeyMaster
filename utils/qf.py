from collections import deque
from enum import IntEnum, auto
import sys

#procedure TRSBusFrameBuilder.Initial( const Event: QEvent );
#begin
#  Q_INIT( NoSettings );
#end;

#constructor TRSBusFrameBuilder.Create;
#begin
#  inherited Create( Initial );
#  Init( EventInit );
#end;


################################################################################

class Signals(IntEnum):
    GET_SUPER = auto()
    INITIALIZE = auto()
    ENTER = auto()
    EXIT = auto()
    LAST = auto()

################################################################################

# rmv Q_EMPTY_SIG  =  0
# rmv Q_INIT_SIG   =  1
# rmv Q_ENTRY_SIG  =  2
# rmv Q_EXIT_SIG   =  3
Q_USER_SIG   = 10


class KeyMasterSignals(IntEnum):
    HARDWARE_CHANGED = Signals.LAST
    SWIPE_10 = auto()
    FRESH_MEMBER_DATA = auto()
    CACHED_MEMBER_DATA = auto()

create_global_events(KeyMasterSignals)
EVENT_SWIPE_10.signal == KeyMasterSignals.SWIPE_10
EVENT_SWIPE_10 == KeyMasterSignals.SWIPE_10
KeyMasterSignals.SWIPE_10 == EVENT_SWIPE_10


#EventInit: QEvent = ( Signal: Q_EMPTY_SIG );

# rmv EVENT_EMPTY = QEvent(Q_EMPTY_SIG)
# rmv EVENT_INIT  = QEvent(Q_INIT_SIG)
# rmv EVENT_ENTRY = QEvent(Q_ENTRY_SIG)
# rmv EVENT_EXIT  = QEvent(Q_EXIT_SIG)

class QHsm():
    def __init__(self, initial_state):
        self._waiting_signals = deque()
        self._first_run = True
        self._initial = initial_state
        self._reset()
    def init(self, event):
        # FIX: Event is always EventInit / EVENT_EMPTY.  Later versions
        # provide a default then eliminate the parameter.  Do the same.
        #
        # HSM not executed yet && we are about to dereference mySource
        # REQUIRE(myState == &QHsm::top && mySource != 0);
        assert self._same_states(self._state, self.top) and (self._source is not None)
        # register QState s = myState;        // save myState in a temporary
        S = self._state
        # (this->*(QPseudoState)mySource)(e); // top-most initial transition
        self._source(event)
        # initial transition must go *one* level deep
        # ASSERT(s == TRIGGER(myState, Q_EMPTY_SIG));
        P = self._get_super_state(self._state)
        assert self._same_states(S, P)
        # s = myState;                               // update the temporary
        S = self._state
        # TRIGGER(s, Q_ENTRY_SIG);                        // enter the state
        S(EVENT_ENTRY)
        # while (TRIGGER(s, Q_INIT_SIG) == 0) {             // init handled?
        while True:
            init_handled = self._state_init(S)
            if init_handled:
                # initial transition must go *one* level deep
                # ASSERT(s == TRIGGER(myState, Q_EMPTY_SIG));
                P = self._get_super_state(self._state)
                assert self._same_states(S, P)
                # s = myState;
                S = self._state
                # TRIGGER(s, Q_ENTRY_SIG);                  // enter the substate
                S(EVENT_ENTRY)
            else:
                break
    def process(self, signal_or_event):
        event = self._wrap_it(signal_or_event)
        rv = False
        if self._internal_process(event):
            rv = True
        while True:
            event = self._get_next_posted_signal()
            if event is None:
                break
            if self._internal_process(event):
                rv = True
    def Q_INIT(self, target):
        self._state = target
        self._finished = False
    def Q_TRAN(self, target):
        # REQUIRE(target != &QHsm::top);        // cannot target "top" state
        assert not self._same_states(target, self.top)
        #for (s = myState; s != mySource; ) {
        #  ASSERT(s != 0);                // we are about to dereference s
        #  QState t = TRIGGER(s, Q_EXIT_SIG);
        #  if (t != 0) {  // exit action unhandled, t points to superstate
        #    s = t;
        #  }
        #  else {                // exit action handled, elicit superstate
        #    s = TRIGGER(s, Q_EMPTY_SIG);
        #  }
        #}
        S = self._state
        while not self._same_states(S, self._source):
            assert S is not None
            T = self._state_exit(S)
            if T is not None:
                S = T
            else:
                S = self._get_super_state(S)
        #*(e = &entry[0]) = 0;
        #*(++e) = target;                         // assume entry to target
        entry = list()
        entry.append(target)
        keep_searching = True
        #// (a) check mySource == target (transition to self)
        #if (mySource == target) {
        #  TRIGGER(mySource, Q_EXIT_SIG);                   // exit source
        #  goto inLCA;
        #}
        if keep_searching and (self._same_states(self._source, target)):
            self._state_exit(self._source)
            keep_searching = False
        #// (b) check mySource == target->super
        #p = TRIGGER(target, Q_EMPTY_SIG);
        #if (mySource == p) {
        #  goto inLCA;
        #}
        if keep_searching:
            P = self._get_super_state(target)
            if self._same_states(self._source, P):
            keep_searching = False;
        #// (c) check mySource->super == target->super (most common)
        #q = TRIGGER(mySource, Q_EMPTY_SIG);
        #if (q == p) {
        #  TRIGGER(mySource, Q_EXIT_SIG);                   // exit source
        #  goto inLCA;
        #}
        if keep_searching:
            Q = self._get_super_state(self._source)
            if self._same_states(Q, P):
                self._state_exit(self._source)
                keep_searching = False
        #// (d) check mySource->super == target
        #if (q == target) {
        #  TRIGGER(mySource, Q_EXIT_SIG);                   // exit source
        #  --e;                                    // do not enter the LCA
        #  goto inLCA;
        #}
        if keep_searching:
            if self._same_states(Q, target):
                self._state_exit(self._source)
                _ = entry.pop()
                keep_searching = False
        #// (e) check rest of mySource == target->super->super... hierarchy
        #*(++e) = p;
        #for (s = TRIGGER(p, Q_EMPTY_SIG); s != 0; s = TRIGGER(s, Q_EMPTY_SIG))
        #{
        #  if (mySource == s) {
        #    goto inLCA;
        #  }
        #  *(++e) = s;
        #}
        #TRIGGER(mySource, Q_EXIT_SIG);                      // exit source
        if keep_searching:
            entry.append(P)
            S := self._get_super_state(P)
            while S is not None:
                if self._same_states(self._source, S):
                    keep_searching = False
                    break
                entry.append(S)
                s = self._get_super_state(S)
            self._state_exit(self._source)
        #// (f) check rest of mySource->super == target->super->super...
        #for (lca = e; *lca != 0; --lca) {
        #  if (q == *lca) {
        #    e = lca - 1;                         // do not enter the LCA
        #    goto inLCA;
        #  }
        #}
        if keep_searching:
            i1 = 1
            for e1 in reversed(entry):
                if self._same_states(Q, e1):
                    while i1 > 0:
                        entry.pop()
                        i1 -= 1
                    keep_searching = False
                    break
                i1 += 1

        if keep_searching:

        if keep_searching:

        # here
    def top(self, event):
        self._event_handled = False
        return None
    def final(self, event):
        if event.signal == Signals.ENTER:
            self._finished = True
            return None
        return self.top
    def _internal_process(self, event):
        self._event_handled = True
        self._source = self._state
        while self._source:
            self._source = self._source(event)
        return self._event_handled
    def _get_next_posted_signal(self):
        if self._waiting_signals:
            return self._waiting_signals.popleft()
        else:
            return None
    def _post_signal(self, signal_or_event):
        self._waiting_signals.append(self._wrap_it(signal_or_event))
    def _reset(self):
        assert self._first_run or self._finished
        self._first_run = True
        self._finished = None
        self._state = self.top
        self._source = self._initial
        self._waiting_signals.clear()
        self._event_handled = None
    @staticmethod
    def _get_super_state(s1):
        return s1(EVENT_GET_SUPER)
    @staticmethod
    def _same_states(s1, s2):
        return s1 == s2
    @staticmethod
    def _state_init(s1):
        return s1(EVENT_INITIALIZE) is None
    @staticmethod
    def _state_exit(s1):
        return s1(EXIT_INIT)
    @staticmethod
    def _wrap_it(signal_or_event):
        if not isinstance(signal_or_event, QEvent):
            return QEvent(signal_or_event)
        else:
            return signal_or_event

class TcpActiveStation(QHsm):
    def __init__(self):
        super().__init__(self.initial)
    def initial(self, event):
        self.Q_INIT(self.no_converter)
    def no_converter(self, event):
        if event.signal == Signals.ENTER:
            # fPort.Close(True)
            return None
        return self.top
