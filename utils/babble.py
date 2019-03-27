"""=============================================================================

  babble for RFID-KeyMaster.
  
  ----------------------------------------------------------------------------


  ----------------------------------------------------------------------------

  Copyright 2019 Brian Cook (aka Coding-Badly)

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
import array
import collections
import copy
import logging
import random

logger = logging.getLogger(__name__)

class MakesWords():
    def __enter__(self):
        self.before_processing()
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        self.after_processing()
        return False
    def before_processing(self):
        pass
    def process(self, word):
        pass
    def after_processing(self):
        pass
    def usable(self):
        return False
    def babble(self):
        return ''

def key_to_chr(key):
    if key >= ' ':
        return key
    else:
        return '_'

def key_part_to_chr(key, shift):
    return key_to_chr(chr((key >> shift) & 0xFF))

class LetterNode():
    def __init__(self, key):
        self._count = 0
        self._key = key
    def process(self):
        self._count += 1
    def __str__(self):
        return "{}: {}".format(key_to_chr(self._key), self._count)

class LetterNodes(dict):
    def __missing__(self, key):
        rv = LetterNode(key)
        self[key] = rv
        return rv

class LetterPairNode():
    def __init__(self, key):
        self._root = LetterNodes()
        self._key = key
    def __str__(self):
        rv = key_part_to_chr(self._key, 8) + key_part_to_chr(self._key, 0) + '\n'
        for node in self._root.values():
            rv += '  ' + str(node) + '\n'
        return rv
    def process(self, character):
        node = self._root[character]
        node.process()

class LetterPairNodes(dict):
    def __missing__(self, key):
        rv = LetterPairNode(key)
        self[key] = rv
        return rv

class TwoLetterTerminal(MakesWords):
    def __init__(self):
        super().__init__()
        self._root = LetterPairNodes()
        self._target_histogram = array.array('L', (0 for i1 in range(16)))
    def __str__(self):
        rv = ''
        for node in self._root.values():
            rv = rv + str(node) + '\n'
        return rv
    def filter(self, word):
        if len(word) <= 1:
            return False
        return True
    def before_processing(self):
        for base in self._root.values():
            base._total = None
    def process(self, word):
        l1 = len(word) - 1
        if l1 >= len(self._target_histogram):
            l1 = len(self._target_histogram) - 1
        self._target_histogram[l1] += 1
        ch3 = chr(0)
        ch2 = chr(0)
        node = self._root
        for ch1 in word:
            index = (ord(ch3) << 8) | (ord(ch2) << 0)
            node = self._root[index]
            node.process(ch1)
            ch3 = ch2
            ch2 = ch1
        index = (ord(ch3) << 8) | (ord(ch2) << 0)
        node = self._root[index]
        node.process(chr(0))
    def after_processing(self):
        for base in self._root.values():
            base._total = sum(node._count for node in base._root.values())
    def usable(self):
        return len(self._root) > 0
    def process_words(self, words):
        for word in words:
            if self.filter(word):
                l1 = len(word) - 1
                if l1 >= len(self._target_histogram):
                    l1 = len(self._target_histogram)
                self._target_histogram[l1] += 1
                ch3 = chr(0)
                ch2 = chr(0)
                node = self._root
                for ch1 in word:
                    index = (ord(ch3) << 8) | (ord(ch2) << 0)
                    node = self._root[index]
                    node.process(ch1)
                    ch3 = ch2
                    ch2 = ch1
                index = (ord(ch3) << 8) | (ord(ch2) << 0)
                node = self._root[index]
                node.process(chr(0))
        for base in self._root.values():
            base._total = sum(node._count for node in base._root.values())
    def babble(self):
        rv = ''
        root = self._root
        ch3 = chr(0)
        ch2 = chr(0)
        while True:
            index = (ord(ch3) << 8) | (ord(ch2) << 0)
            base = root[index]
            pick_value = random.randrange(base._total)
            previous = 0
            for node in base._root.values():
                next = previous + node._count
                if (pick_value >= previous) and (pick_value < next):
                    pick = node
                    break
                previous = next
            if pick._key == chr(0):
                break
            rv += pick._key
            ch3 = ch2
            ch2 = pick._key
        return rv

class WordSequence(MakesWords):
    def __init__(self):
        super().__init__()
        self._correlations = collections.defaultdict(collections.Counter)
        self._correlations_totals = collections.Counter()
        self._lengths = collections.Counter()
        self._lengths_total = 0
    def before_processing(self):
        for key in self._correlations_totals.keys():
            self._correlations_totals[key] = 0
        self._lengths_total = 0
    def process(self, member_groups):
        self._correlations[0].update(member_groups)
        for group in member_groups:
            self._correlations[group].update(member_groups)
        self._lengths[len(member_groups)] += 1
    def after_processing(self):
        for group in self._correlations.keys():
            correlation = self._correlations[group]
            del correlation[group]
            self._correlations_totals[group] = sum(count for count in correlation.values())
        self._lengths_total = sum(count for count in self._lengths.values())
    def usable(self):
        return self._lengths_total > 0
    def babble(self):
        rv = set()
        pick_length = random.randrange(self._lengths_total)
        cumulative = 0
        for key in self._lengths.keys():
            cumulative += self._lengths[key]
            if pick_length < cumulative:
                rv_target_length = key
                break
        previous = 0
        next = 0
        while len(rv) < rv_target_length:
            correlation = self._correlations[previous]
            total = self._correlations_totals[previous]
            pick = random.randrange(total)
            cumulative = 0
            for key in correlation.keys():
                cumulative += correlation[key]
                if pick < cumulative:
                    next = key
                    break
            rv.add(next)
            previous = next
        return rv

class BabblerFilter():
    def filter_for_process(self, word):
        return True
    def filter_for_return(self, word):
        return True
    def was_returned(self, word):
        pass
    def before_processing(self, makes_words):
        pass
    def after_processing(self, parent):
        pass
    def notify(self, what, **kwargs):
        pass

class BabblerFilterNotTooShort(BabblerFilter):
    def filter_for_process(self, word):
        return len(word) >= 2
    def notify(self, what, **kwargs):
        if what == 'tidy_target_histogram':
            histogram = kwargs['histogram']
            histogram[0] = 0
            histogram[1] = 0

class BabblerFilterDontUseThese(BabblerFilter):
    def __init__(self, dont_use_these):
        self._dont_use_these = dont_use_these
    def filter_for_return(self, word):
        return not (word in self._dont_use_these)

class BabblerFilterMatchHistogram(BabblerFilter):
    def __init__(self):
        self._reset_actual_histogram()
        self._chance_to_keep = array.array('d', (1.0 for i1 in range(16)))
    def _reset_actual_histogram(self):
        self._actual_histogram = array.array('L', (0 for i1 in range(16)))
    def filter_for_return(self, word):
        l1 = len(word) - 1
        if l1 >= len(self._chance_to_keep):
            return False
        return random.random() < self._chance_to_keep[l1]
    def was_returned(self, word):
        l1 = len(word) - 1
        if l1 >= len(self._actual_histogram):
            l1 = len(self._actual_histogram) - 1
        self._actual_histogram[l1] += 1
    def scale_histogram_to_per_million(self, histogram):
        total = sum(value for value in histogram)
        for i1 in range(len(histogram)):
            histogram[i1] = int(round(1000000 * histogram[i1] / total))
    def after_processing(self, parent):
        if parent.usable():
            for i1 in range(100000):
                word = parent.babble()
            t1 = parent.get_target_histogram()
            t2 = self.get_actual_histogram()
            parent.notify_all_filters( 'tidy_target_histogram', histogram=t1)
            parent.notify_all_filters( 'tidy_target_histogram', histogram=t2)
            self.scale_histogram_to_per_million(t1)
            self.scale_histogram_to_per_million(t2)
            ratios = array.array('d', (target/actual if actual > 0 else 0 for target, actual in zip(t1, t2)))
            maximum = max(value for value in ratios)
            self._chance_to_keep = array.array('d', (ratio/maximum for ratio in ratios))
            self._reset_actual_histogram()
    def get_actual_histogram(self):
        return copy.copy(self._actual_histogram)

class FilteredBabbler():
    def __init__(self, makes_words):
        self._makes_words = makes_words
        self._filters = list()
    def add_filter(self, filter):
        self._filters.append(filter)
    def notify_all_filters(self, what, **kwargs):
        for filter in self._filters:
            filter.notify(what, **kwargs)
    def process(self, words):
        with self._makes_words as makes_words:
            for filter in self._filters:
                filter.before_processing(makes_words)
            for word in words:
                for filter in self._filters:
                    if not filter.filter_for_process(word):
                        continue
                makes_words.process(word)
        # fix? No notification if an exception occurs.
        for filter in self._filters:
            filter.after_processing(self)
    def usable(self):
        return self._makes_words.usable()
    def babble(self):
        if self._makes_words.usable():
            GoAgain = True
            while GoAgain:
                GoAgain = False
                rv = self._makes_words.babble()
                for filter in self._filters:
                    if not filter.filter_for_return(rv):
                        GoAgain = True
                        continue
            for filter in self._filters:
                filter.was_returned(rv)
        else:
            rv = ''
        return rv
    def get_target_histogram(self):
        return copy.copy(self._makes_words._target_histogram)

