from collections import deque

#EventInit: QEvent = ( Signal: Q_EMPTY_SIG );

#procedure TRSBusFrameBuilder.Initial( const Event: QEvent );
#begin
#  Q_INIT( NoSettings );
#end;

#constructor TRSBusFrameBuilder.Create;
#begin
#  inherited Create( Initial );
#  Init( EventInit );
#end;


Q_EMPTY_SIG  =  0
Q_INIT_SIG   =  1
Q_ENTRY_SIG  =  2
Q_EXIT_SIG   =  3
Q_USER_SIG   = 10

class QEvent():
    def __init__(self, signal):
        self.signal = signal

class QHsm():
    def __init__(self, initial_state):
        self._waiting_signals = deque()
        self._first_run = True
        self._initial = initial_state
        self._reset()
    def init(self, event):
        assert self._same_states(self._state, self.top) and (self._source is not None)
        S := self._state
        self._source(event)
        P := GetSuperState(self._state)
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
    def top(self, event):
        self._event_handled = False
        return None
    def final(self, event):
        if event.signal == Q_ENTRY_SIG:
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
    @staticmethod
    def _wrap_it(signal_or_event):
        if not isinstance(signal_or_event, QEvent):
            return QEvent(signal_or_event)
        else:
            return signal_or_event
    def _reset(self):
        assert self._first_run or self._finished
        self._first_run = True
        self._finished = None
        self._state = self.top
        self._source = self._initial
        self._waiting_signals.clear()
        self._event_handled = None
    @staticmethod
    def _same_states(s1, s2):
        return s1 == s2

class TcpActiveStation(QHsm):
    def __init__(self):
        super().__init__(self.initial)
    def initial(self, event):
        self.Q_INIT(self.no_converter)
    def no_converter(self, event):
        if event.signal == Q_ENTRY_SIG:
            # fPort.Close(True)
            return None
        return self.top
