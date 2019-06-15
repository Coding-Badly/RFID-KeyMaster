"""=============================================================================

  StateMachine for RFID-KeyMaster.  StateMachine is a base class for
  hierarchical state machines.  It's based on the strategy and structure
  described in Practical UML Statecharts in C/C++.

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
import abc
import collections
import enum
import logging
from statemachine.signals import (
    create_state_machine_events, 
    Signals, 
    StateMachineEvent)

logger = logging.getLogger(__name__)

class MalformedStateMachineError(Exception):
    pass

class TopCannotBeTargetError(MalformedStateMachineError):
    pass

class InvalidInternalStateInInitializeError(MalformedStateMachineError):
    pass

create_state_machine_events(Signals, __name__)

class StateMachine(abc.ABC):
    def __init__(self):
        self._waiting_signals = collections.deque()
        self._first_run = True
        self._path_to_top = dict()
        # fix: Don't bother storing _initial
        # rmv self._initial = self._get_initial_state()
        self._reset()
        self._after_init()
    def _after_init(self):
        pass
    @abc.abstractmethod
    def _get_initial_state(self):
        return None
    def _top_state(self, event):
        if event == Signals.GET_SUPER_STATE:
            return None
        self._event_handled = False
        return None
    def _final_state(self, event):
        if event == Signals.ENTER_STATE:
            self._finished = True
            return None
        return self._top_state
    def _initial_transition(self, target):
        self._state = target
    def _initialize_from_state(self):
        s1 = self._state
        while self._state_init(s1):
            s2 = self._state
            if not self._same_states(s1, self._get_super_state(s2)):
                raise InvalidInternalStateInInitializeError()
            s1 = s2
            self._state_enter(s1)
    def initialize_machine(self):
        if self._state != self._top_state:
            raise InvalidInternalStateInInitializeError()
        if self._source is None:
            raise InvalidInternalStateInInitializeError()
        s1 = self._state
        self._state_init(self._source)
        p1 = self._get_super_state(self._state)
        if not self._same_states(s1, p1):
            raise InvalidInternalStateInInitializeError()
        self._state_enter(self._state)
        self._initialize_from_state()
        #s1 = self._state
        #s1(EVENT_ENTER_STATE)
        #while True:
        #    init_handled = self._state_init(s1)
        #    if init_handled:
        #        p1 = self._get_super_state(self._state)
        #        assert self._same_states(s1, p1)
        #        # fix self._state_enter(self._state)
        #        s1 = self._state
        #        s1(EVENT_ENTER_STATE)
        #    else:
        #        break
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
        return rv
    @staticmethod
    def _get_super_state(s1):
        return s1(EVENT_GET_SUPER_STATE)
    @staticmethod
    def _same_states(s1, s2):
        return s1 == s2
    def _state_enter(self, s1):
        rv = s1(EVENT_ENTER_STATE)
        self._state = s1
        # rmv return rv
    def _state_exit(self, s1):
        if not self._same_states(s1, self._state):
            raise MalformedStateMachineError()
        rv = s1(EVENT_EXIT_STATE)
        self._state = rv if rv is not None else self._get_super_state(s1)
        # rmv return rv
    @staticmethod
    def _state_init(s1):
        return s1(EVENT_INITIALIZE_STATE) is None
    @staticmethod
    def _wrap_it(signal_or_event):
        if not isinstance(signal_or_event, StateMachineEvent):
            return StateMachineEvent(signal_or_event)
        else:
            return signal_or_event
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
        self._state = self._top_state
        self._source = self._initial_pseudo_state
        self._waiting_signals.clear()
        self._event_handled = None
    def _initial_pseudo_state(self, event):
        if event != Signals.INITIALIZE_STATE:
            raise InvalidInternalStateInInitializeError()
        self._initial_transition(self._get_initial_state())
        return self._top_state
    def _internal_process(self, event):
        self._event_handled = True
        self._source = self._state
        while self._source:
            self._source = self._source(event)
        return self._event_handled
    def _get_path_to_top(self, start):
        path_to_top = []
        rover = start
        while rover is not None:
            path_to_top.append(rover)
            rover = self._get_super_state(rover)
        return path_to_top
    def _get_path_to_top_cached(self, cache, start):
        path_to_top = cache.get(start, None)
        if path_to_top is None:
            #logger.info('Determine path to top for {}.'.format(start))
            path_to_top = self._get_path_to_top(start)
            #cache[start] = path_to_top
        return path_to_top
    def _transition(self, target):
        if self._same_states(target, self._top_state):
            raise TopCannotBeTargetError()
        # Exit all states from _state to _source
        while not self._same_states(self._state, self._source):
            #logger.info('State Exit: {}'.format(self._state))
            self._state_exit(self._state)
        # Transition to the current state is a special case.
        if self._same_states(target, self._state):
            self._state_exit(self._state)
            self._state_enter(target)
        # Otherwise the transition is exit to LCA then enter to target.
        else:
            # Fetch / build paths from each end to _top_state
            ptt = self._path_to_top
            source_to_top = self._get_path_to_top_cached(ptt, self._source)
            target_to_top = self._get_path_to_top_cached(ptt, target)
            #logger.info([f.__func__.__name__ for f in source_to_top])
            #logger.info([f.__func__.__name__ for f in target_to_top])
            # Find the least common ancestor (LCA) by searching the two lists back-to-front
            fi = len(source_to_top) - 1
            ti = len(target_to_top) - 1
            if not self._same_states(source_to_top[fi], self._top_state) \
                    or not self._same_states(target_to_top[ti], self._top_state):
                raise MalformedStateMachineError()
            while (fi > -1) and (ti > -1):
                if source_to_top[fi] != target_to_top[ti]:
                    break
                fi -= 1
                ti -= 1
            # LCA is the previous pair (fi+1, ti+1)
            fi += 1
            ti += 1
            if source_to_top[fi] != target_to_top[ti]:
                raise MalformedStateMachineError()
            #logger.info('fi={}, ti={}'.format(fi, ti))
            # Exit all states from _source (inclusive) to LCA (exclusive)
            for i1 in range(0, fi):
                # rmv s1 = source_to_top[i1].__get__(self, self.__class__)
                # rmv logger.info('----------')
                #logger.info('#{}: X: {}'.format(i1, source_to_top[i1]))
                # rmv logger.info('#{}: {}'.format(i1, s1))
                # rmv logger.info('----------')
                self._state_exit(source_to_top[i1])
            for i1 in range(ti-1, -1, -1):
                #logger.info('#{}: N: {}'.format(i1, target_to_top[i1]))
                self._state_enter(target_to_top[i1])
            if not self._same_states(self._state, target):
                raise MalformedStateMachineError()
        self._initialize_from_state()
    def _is_in(self, state):
        rover = self._state
        while rover is not None:
            if self._same_states(rover, state):
                return True
            rover = self._get_super_state(rover)
        return False
