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
    """MakesWords is a base class for things that analyze raw data (like a list of names) then
    output random words resembling what was analyzed.
    """
    def __enter__(self):
        self.before_analyze()
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        self.after_analyze()
        return False
    def before_analyze(self):
        """Called before analyze so any resources can be prepared / any data can be initialized.
        This method primarily exists as a convenience so the developer does not have to deal
        with __enter__.
        """
    def analyze(self, raw_data):
        """Analyze raw_data and update the internal state.
        """
    def after_analyze(self):
        """Called after analyze so any resources can be released / any cleanup performed.  This
        method primarily exists as a convenience so the developer does not have to deal with
        __exit__.
        """
    def usable(self):
        """Return True if the object is ready to babble.
        """
        # pylint: disable=no-self-use
        return False
    def babble(self):
        """Return one randomly generated thing that is expected to be similar to the raw_data that
        was passed to analyze.
        """
        # pylint: disable=no-self-use
        return ''

def key_to_chr(key):
    """Ensure the passed key (a character) is printable.
    """
    # pylint: disable=no-else-return
    if key >= ' ':
        return key
    else:
        return '_'

def key_part_to_chr(key, shift):
    """Ensure the key part (essentially a byte) is printable.
    """
    return key_to_chr(chr((key >> shift) & 0xFF))

class LetterNode():
    """A terminal / leaf in the TwoLetterTerminal data structure.  The count of letter occurances
    at this point in the tree is kept.
    """
    def __init__(self, key):
        self._count = 0
        self._key = key
    def update_count(self):
        """Update the internal state.  In this case that consists of incrementing the letter count.
        """
        self._count += 1
    def __str__(self):
        return "{}: {}".format(key_to_chr(self._key), self._count)

class LetterNodes(dict):
    """A dictionary of LetterNode.
    """
    def __missing__(self, key):
        rv = LetterNode(key)
        self[key] = rv
        return rv

class LetterPairNode():
    """An interior node in the TwoLetterTerminal data structure.  Interior nodes are a letter
    pair (digraph) leading to a histogram of the next letters.
    """
    def __init__(self, key):
        self._root = LetterNodes()
        self._key = key
    def __str__(self):
        rv = key_part_to_chr(self._key, 8) + key_part_to_chr(self._key, 0) + '\n'
        for node in self._root.values():
            rv += '  ' + str(node) + '\n'
        return rv
    def analyze(self, character):
        """Find the LetterNode for the character and update the count.
        """
        node = self._root[character]
        node.update_count()

class LetterPairNodes(dict):
    """A dictionary of LetterPairNode.
    """
    def __missing__(self, key):
        rv = LetterPairNode(key)
        self[key] = rv
        return rv

class TwoLetterTerminal(MakesWords):
    """TwoLetterTerminal creates histograms of digraphs then generates random words with similar
    digraphs.
    """
    # pylint: disable=protected-access
    def __init__(self):
        super().__init__()
        self._root = LetterPairNodes()
        self._target_histogram = array.array('L', (0 for i1 in range(16)))
    def __str__(self):
        rv = ''
        for node in self._root.values():
            rv = rv + str(node) + '\n'
        return rv
    def filter_word(self, word):
        """Only allow words at least two characters in length.
        """
        # pylint: disable=no-self-use
        if len(word) <= 1:
            return False
        return True
    def before_analyze(self):
        """Reset the total.
        """
        for base in self._root.values():
            base._total = None
    def analyze(self, raw_data):
        """For every diagraph keep a histogram of the next letter.
        """
        le1 = len(raw_data) - 1
        if le1 >= len(self._target_histogram):
            le1 = len(self._target_histogram) - 1
        self._target_histogram[le1] += 1
        ch3 = chr(0)
        ch2 = chr(0)
        node = self._root
        for ch1 in raw_data:
            index = (ord(ch3) << 8) | (ord(ch2) << 0)
            node = self._root[index]
            node.analyze(ch1)
            ch3 = ch2
            ch2 = ch1
        index = (ord(ch3) << 8) | (ord(ch2) << 0)
        node = self._root[index]
        node.analyze(chr(0))
    def after_analyze(self):
        """Update the total.
        """
        for base in self._root.values():
            base._total = sum(node._count for node in base._root.values())
    def usable(self):
        """We can only babble after some analyzing.
        """
        return len(self._root) > 0
    def analyze_words(self, words):
        """Deprecated.
        """
        for word in words:
            if self.filter_word(word):
                le1 = len(word) - 1
                if le1 >= len(self._target_histogram):
                    le1 = len(self._target_histogram)
                self._target_histogram[le1] += 1
                ch3 = chr(0)
                ch2 = chr(0)
                node = self._root
                for ch1 in word:
                    index = (ord(ch3) << 8) | (ord(ch2) << 0)
                    node = self._root[index]
                    node.analyze(ch1)
                    ch3 = ch2
                    ch2 = ch1
                index = (ord(ch3) << 8) | (ord(ch2) << 0)
                node = self._root[index]
                node.analyze(chr(0))
        for base in self._root.values():
            base._total = sum(node._count for node in base._root.values())
    def babble(self):
        """Return one randomly generated word with a letter sequence similar to the words
        that were analyzed.
        """
        rv = ''
        root = self._root
        ch3 = chr(0)
        ch2 = chr(0)
        while True:
            index = (ord(ch3) << 8) | (ord(ch2) << 0)
            base = root[index]
            pick_value = random.randrange(base._total)
            previous_mark = 0
            for node in base._root.values():
                next_mark = previous_mark + node._count
                if previous_mark <= pick_value < next_mark:
                    pick = node
                    break
                previous_mark = next_mark
            if pick._key == chr(0):
                break
            rv += pick._key
            ch3 = ch2
            ch2 = pick._key
        return rv

class WordSequence(MakesWords):
    """WordSequence determines word correlations then generates random sequences with similar
    patterns.
    """
    def __init__(self):
        super().__init__()
        self._correlations = collections.defaultdict(collections.Counter)
        self._correlations_totals = collections.Counter()
        self._lengths = collections.Counter()
        self._lengths_total = 0
    def before_analyze(self):
        """Reset the totals.
        """
        for key in self._correlations_totals.keys():
            self._correlations_totals[key] = 0
        self._lengths_total = 0
    def analyze(self, raw_data):
        """For each word (group) in raw_data update a histogram of the other words (groups) in
        raw_data.
        """
        self._correlations[0].update(raw_data)
        for group in raw_data:
            self._correlations[group].update(raw_data)
        self._lengths[len(raw_data)] += 1
    def after_analyze(self):
        """Update the totals.
        """
        for group in self._correlations.keys():
            correlation = self._correlations[group]
            del correlation[group]
            self._correlations_totals[group] = sum(count for count in correlation.values())
        self._lengths_total = sum(count for count in self._lengths.values())
    def usable(self):
        """This thing is usable if at least one count is greater than zero.
        """
        return self._lengths_total > 0
    def babble(self):
        """Return a word sequence that resembles analyzed word sequences.
        """
        rv = set()
        pick_length = random.randrange(self._lengths_total)
        cumulative = 0
        for key in self._lengths.keys():
            cumulative += self._lengths[key]
            if pick_length < cumulative:
                rv_target_length = key
                break
        previous_key = 0
        next_key = 0
        while len(rv) < rv_target_length:
            correlation = self._correlations[previous_key]
            total = self._correlations_totals[previous_key]
            pick = random.randrange(total)
            cumulative = 0
            for key in correlation.keys():
                cumulative += correlation[key]
                if pick < cumulative:
                    next_key = key
                    break
            rv.add(next_key)
            previous_key = next_key
        return rv

class BabblerFilter():
    """Provide a way to filter, post process, and evaluate a babbles.
    """
    def filter_for_analyze(self, word):
        # pylint: disable=no-self-use
        # pylint: disable=unused-argument
        """Called before raw data is passed to analyze.  Returning False results in the raw data
        being skipped / ignored.
        """
        return True
    def filter_for_return(self, word):
        # pylint: disable=no-self-use
        # pylint: disable=unused-argument
        """Called before a babble is returned.  Returning False results in the babble being
        discarded and another attempt is made to generate a returnable babble.
        """
        return True
    def was_returned(self, word):
        """Called before a babble is returned.  This method is an opportunity for a filter to make
        adjustments based on what is actually being generated.
        """
    def before_analyze(self, makes_words):
        """Called before a set of raw data is passed to analyze.  This method is an opportunity to
        prepare for a series of calls to filter_for_analyze.
        """
    def after_analyze(self, parent):
        """Called after a set of raw data has been passed to analyze.  This method is an
        opportunity to clean up anything done in before_analyze.
        """
    def notify(self, what, **kwargs):
        """Inter-filter communications.  This method is called from notify_all_filters.  It allows
        filters to broadcast messages to other filters.
        """

class BabblerFilterNotTooShort(BabblerFilter):
    """This filter blocks words less than two characters from being analyzed.
    """
    def filter_for_analyze(self, word):
        """Only analyze words with at least two characters.
        """
        return len(word) >= 2
    def notify(self, what, **kwargs):
        """Ensure any histograms have zeros for zero and one character buckets.
        """
        if what == 'tidy_target_histogram':
            histogram = kwargs['histogram']
            histogram[0] = 0
            histogram[1] = 0

class BabblerFilterDontUseThese(BabblerFilter):
    """This filter blocks "real" words from being returned from babble.  A good example is a
    babble meant to generate first names similar to the first names of people in the U.S.
    Ideally, such a babble never returns actual first names.  This filter is a piece of that
    solution.
    """
    def __init__(self, dont_use_these):
        self._dont_use_these = dont_use_these
    def filter_for_return(self, word):
        """Do not return words in our "don't use these" list.
        """
        return not word in self._dont_use_these

class BabblerFilterMatchHistogram(BabblerFilter):
    """This filter creates a histogram of word lengths of the analyzed data then filters the output
    of babble to match.
    """
    def __init__(self):
        self._reset_actual_histogram()
        self._chance_to_keep = array.array('d', (1.0 for i1 in range(16)))
    def _reset_actual_histogram(self):
        self._actual_histogram = array.array('L', (0 for i1 in range(16)))
    def filter_for_return(self, word):
        """Roll the dice to determine if a word of that length should be returned or discarded.
        """
        le1 = len(word) - 1
        if le1 >= len(self._chance_to_keep):
            return False
        return random.random() < self._chance_to_keep[le1]
    def was_returned(self, word):
        """Track the lengths of the returned words.
        """
        le1 = len(word) - 1
        if le1 >= len(self._actual_histogram):
            le1 = len(self._actual_histogram) - 1
        self._actual_histogram[le1] += 1
    def scale_histogram_to_per_million(self, histogram):
        """Scale the values so they can be stored as int with minimal loss of precision.
        """
        # pylint: disable=no-self-use
        # pylint: disable=consider-using-enumerate
        total = sum(value for value in histogram)
        for ix1 in range(len(histogram)):
            histogram[ix1] = int(round(1000000 * histogram[ix1] / total))
    def after_analyze(self, parent):
        """After analyzing collect results from babble to estimate how well this filter will
        perform.
        """
        if parent.usable():
            for _ in range(100000):
                parent.babble()
            te1 = parent.get_target_histogram()
            te2 = self.get_actual_histogram()
            parent.notify_all_filters('tidy_target_histogram', histogram=te1)
            parent.notify_all_filters('tidy_target_histogram', histogram=te2)
            self.scale_histogram_to_per_million(te1)
            self.scale_histogram_to_per_million(te2)
            ratios = array.array('d', \
                    (target/actual if actual > 0 else 0 for target, actual in zip(te1, te2)))
            maximum = max(value for value in ratios)
            self._chance_to_keep = array.array('d', (ratio/maximum for ratio in ratios))
            self._reset_actual_histogram()
    def get_actual_histogram(self):
        """Return a histogram of the lengths that have been returned from babble.
        """
        return copy.copy(self._actual_histogram)

class FilteredBabbler():
    """A babbler capable of being filtered.
    """
    def __init__(self, makes_words):
        self._makes_words = makes_words
        self._filters = list()
    def add_filter(self, babble_filter):
        """Add a filter.
        """
        self._filters.append(babble_filter)
    def notify_all_filters(self, what, **kwargs):
        """Broadcast a message to all filters.
        """
        for fi1 in self._filters:
            fi1.notify(what, **kwargs)
    def analyze(self, words):
        """Analyze a list of words.
        """
        with self._makes_words as makes_words:
            for fi1 in self._filters:
                fi1.before_analyze(makes_words)
            for word in words:
                for fi1 in self._filters:
                    if not fi1.filter_for_analyze(word):
                        continue
                makes_words.analyze(word)
        # fix? No notification if an exception occurs.
        for fi1 in self._filters:
            fi1.after_analyze(self)
    def usable(self):
        """Is this babbler usable?
        """
        return self._makes_words.usable()
    def babble(self):
        """Attempt to create a babble based on the generator (makes_words) and the filters.
        """
        if self._makes_words.usable():
            go_again = True
            while go_again:
                go_again = False
                rv = self._makes_words.babble()
                for fi1 in self._filters:
                    if not fi1.filter_for_return(rv):
                        go_again = True
                        continue
            for fi1 in self._filters:
                fi1.was_returned(rv)
        else:
            rv = ''
        return rv
    def get_target_histogram(self):
        """Return the target histogram for debugging purposes.
        """
        # pylint: disable=protected-access
        return copy.copy(self._makes_words._target_histogram)
