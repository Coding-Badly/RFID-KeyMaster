import array
from utils.babble import BabblerFilterDontUseThese, BabblerFilterMatchHistogram, BabblerFilterNotTooShort, FilteredBabbler, TwoLetterTerminal, WordSequence
import collections
import copy
import csv
import logging
import os
from pathlib import Path
import pytest
import pyzipper
import random
from utils.superglob import SuperGlobAndOpen, ENVIRONMENT_VARIABLE_PREFIX, clean_stem_to_simple_environment_variable
import textwrap
import yaml

logger = logging.getLogger(__name__)

################################################################################

def get_employee_id_set(load_these=None):
    if load_these is None:
        load_these = SuperGlobAndOpen(skip_if_not_exists=True, empty_if_bad_password=True)
        load_these.add(Path('Employee IDs.zip'))
    rv = set()
    for load_this in load_these:
        if load_this.name.suffix.lower() == '.txt':
            with load_this.open() as inf:
                reader = csv.reader(inf)
                for row in reader:
                    if len(row) > 0:
                        rv.add(row[0].upper())
    return rv

@pytest.fixture(scope="session")
def load_these_employee_ids():
    load_these = SuperGlobAndOpen(skip_if_not_exists=True, empty_if_bad_password=True)
    load_these.add(Path('Does Not Exist.txt'))
    load_these.add(Path('Employee IDs.zip'))
    load_these.add(Path('Does Not Exist.zip'))
    return load_these

@pytest.fixture(scope="session")
def employee_ids(load_these_employee_ids):
    return get_employee_id_set(load_these_employee_ids)

def test_get_employee_id_set(caplog, employee_ids):
    caplog.set_level(logging.INFO)
    logger.info("%d employee IDs.", len(employee_ids))

def test_employee_id_babble(caplog, employee_ids):
    caplog.set_level(logging.INFO)
    tm3 = FilteredBabbler(TwoLetterTerminal())
    tm3.add_filter(BabblerFilterDontUseThese(employee_ids))
    tm4 = BabblerFilterMatchHistogram()
    tm3.add_filter(tm4)
    tm3.process(employee_ids)
    if tm3.usable():
        dump_histogram(tm3._makes_words._target_histogram)
        for i1 in range(100000):
            word = tm3.babble()
        dump_histogram(tm4._actual_histogram)
        for i1 in range(20):
            word = tm3.babble()
            logger.info("{}, {}".format(word, word in employee_ids))
        filename = Path('Employee IDs Babble.zip')
        envarname = ENVIRONMENT_VARIABLE_PREFIX + clean_stem_to_simple_environment_variable(filename.stem)
        password = os.getenv(envarname, None)
        if password:
            with pyzipper.AESZipFile(filename, 'w', compression=pyzipper.ZIP_LZMA, encryption=pyzipper.WZ_AES) as zip:
                zip.pwd = password
                with zip.open('Employee IDs Babble.yaml', 'w') as ouf:
                    yaml.dump(tm3, ouf, encoding='utf-8')

################################################################################

def get_first_name_sets(load_these=None):
    if load_these is None:
        load_these = SuperGlobAndOpen(skip_if_not_exists=True, empty_if_bad_password=True)
        load_these.add(Path('First Names from Social Security Administration.zip'))
        load_these.add(Path('First Names from DMS.zip'))
    girls = set()
    boys = set()
    for load_this in load_these:
        if load_this.name.suffix.lower() == '.txt':
            with load_this.open() as inf:
                reader = csv.reader(inf)
                for row in reader:
                    if len(row) > 0:
                        if len(row) >= 3:
                            if row[1] == 'F':
                                girls.add(row[0])
                            if row[1] == 'M':
                                boys.add(row[0])
                        else:
                            girls.add(row[0])
                            boys.add(row[0])
    return (girls, boys)

@pytest.fixture(scope="session")
def load_these_first_name_sets():
    load_these = SuperGlobAndOpen(skip_if_not_exists=True, empty_if_bad_password=True)
    load_these.add(Path('Does Not Exist.txt'))
    load_these.add(Path('Does Not Exist.zip'))
    load_these.add(Path('First Names from Social Security Administration.zip'))
    load_these.add(Path('First Names from DMS.zip'))
    return load_these

@pytest.fixture(scope="session")
def first_name_sets(load_these_first_name_sets):
    return get_first_name_sets(load_these_first_name_sets)

@pytest.fixture(scope="session")
def girls(first_name_sets):
    return first_name_sets[0]

@pytest.fixture(scope="session")
def boys(first_name_sets):
    return first_name_sets[1]

@pytest.fixture(scope="session", params=['girls', 'boys'])
def each_gender(request, first_name_sets):
    return first_name_sets[0] if request.param == 'girls' else first_name_sets[1]

def x_test_get_first_name_sets(caplog, first_name_sets):
    caplog.set_level(logging.INFO)
    girls, boys = first_name_sets
    logger.info("%d girls.  %d boys.", len(girls), len(boys))

def x_test_get_first_name(caplog, each_gender):
    caplog.set_level(logging.INFO)
    logger.info("%d names.", len(each_gender))

def x_test_first_name_babble(caplog, each_gender):
    caplog.set_level(logging.INFO)
    tm3 = FilteredBabbler(TwoLetterTerminal())
    tm3.add_filter(BabblerFilterNotTooShort())
    tm3.add_filter(BabblerFilterDontUseThese(each_gender))
    tm4 = BabblerFilterMatchHistogram()
    tm3.add_filter(tm4)
    tm3.process(each_gender)
    dump_histogram(tm3._makes_words._target_histogram)
    for i1 in range(100000):
        word = tm3.babble()
    dump_histogram(tm4._actual_histogram)
    for i1 in range(20):
        word = tm3.babble()
        logger.info("{}, {}".format(word, word in each_gender))

################################################################################

def get_last_name_set(load_these=None):
    if load_these is None:
        load_these = SuperGlobAndOpen(skip_if_not_exists=True, empty_if_bad_password=True)
        load_these.add(Path('Last Names from Census Bureau.zip'))
        load_these.add(Path('Last Names from DMS.zip'))
    rv = set()
    for load_this in load_these:
        if load_this.name.suffix.lower() == '.txt':
            with load_this.open() as inf:
                reader = csv.reader(inf)
                for row in reader:
                    if len(row) > 0:
                        rv.add(row[0].upper())
    return rv

@pytest.fixture(scope="session")
def load_these_last_names():
    load_these = SuperGlobAndOpen(skip_if_not_exists=True, empty_if_bad_password=True)
    load_these.add(Path('Last Names from Census Bureau.zip'))
    load_these.add(Path('Last Names from DMS.zip'))
    load_these.add(Path('Does Not Exist.txt'))
    load_these.add(Path('Does Not Exist.zip'))
    return load_these

@pytest.fixture(scope="session")
def last_names(load_these_last_names):
    return get_last_name_set(load_these_last_names)

def x_test_get_last_name_set(caplog, last_names):
    caplog.set_level(logging.INFO)
    logger.info("%d last names.", len(last_names))

def x_test_last_name_babble(caplog, last_names):
    caplog.set_level(logging.INFO)
    tm3 = FilteredBabbler(TwoLetterTerminal())
    tm3.add_filter(BabblerFilterNotTooShort())
    tm3.add_filter(BabblerFilterDontUseThese(last_names))
    tm4 = BabblerFilterMatchHistogram()
    tm3.add_filter(tm4)
    tm3.process(last_names)
    dump_histogram(tm3._makes_words._target_histogram)
    for i1 in range(100000):
        word = tm3.babble()
    dump_histogram(tm4._actual_histogram)
    for i1 in range(20):
        word = tm3.babble()
        logger.info("{}, {}".format(word, word in last_names))

################################################################################

def generate_all_group_combinations(load_these=None):
    if load_these is None:
        load_these = SuperGlobAndOpen(skip_if_not_exists=True, empty_if_bad_password=True)
        load_these.add(Path('Group Combinations from DMS.zip'))
    for load_this in load_these:
        with load_this.open() as inf:
            member_groups = set()
            reader = csv.reader(inf)
            for row in reader:
                if len(row) == 0:
                    if len(member_groups) > 0:
                        yield member_groups
                        member_groups.clear()
                else:
                    common_name = get_common_name(row)
                    if common_name:
                        # 'Domain Users' and 'Members' appears to be implied.
                        # Don't bother with them.
                        if common_name != 'Domain Users':
                            if common_name != 'Members':
                                member_groups.add(common_name)
            if len(member_groups) > 0:
                yield member_groups
                member_groups.clear()
              
def x_test_generate_all_group_combinations(caplog):
    caplog.set_level(logging.INFO)
    load_these = SuperGlobAndOpen(skip_if_not_exists=True, empty_if_bad_password=True)
    load_these.add(Path('Does Not Exist.txt'))
    load_these.add(Path('Group Combinations from DMS.zip'))
    load_these.add(Path('Does Not Exist.zip'))
    total_combinations = 0
    total_entries = 0
    for member_groups in generate_all_group_combinations():
        total_combinations += 1
        total_entries += len(member_groups)
        if (random.random() < 10.0/3163.0):
            logger.info(member_groups)
    logger.info("%d combinations.  %d entries", total_combinations, total_entries)

def x_test_WordSequence_001(caplog):
    caplog.set_level(logging.INFO)
    tm1 = FilteredBabbler(WordSequence())
    tm1.process(generate_all_group_combinations())
    for i1 in range(10):
        rv1 = tm1.babble()
        rv1.add('Members')
        logger.info(rv1)

################################################################################
################################################################################
################################################################################

def dump_histogram(histogram):
    logger.info("-----")
    total = 0
    for value in histogram:
        total += value
    length = 1
    for value in histogram:
        logger.info("{0:2}:  {1:7.3f}%  {2:6}".format(length, 100.0*value/total, value))
        length += 1
    logger.info("-----")

def dump_probabilities(table):
    logger.info("-----")
    length = 1
    for value in table:
        logger.info("{0:2}:  {1:5.3f}".format(length, value))
        length += 1
    logger.info("-----")

def scale_histogram_to_per_million(histogram):
    rv = copy.copy(histogram)
    total = sum(value for value in rv)
    for i1 in range(len(rv)):
        rv[i1] = int(round(1000000 * rv[i1] / total))
    return rv

def x_test_003(caplog):
    caplog.set_level(logging.INFO)
    girls, boys = get_first_name_sets()
    logger.info("------------------------------------------------------------")
    #tm1 = TwoLetterTerminal()
    #tm1.process_words(girls)
    #logger.info("{} girls".format(len(girls)))
    #for i1 in range(100):
    #    word = tm1.babble()
    #    logger.info("{}, {}".format(word, word in girls))
    #dump_histogram(tm1._target_histogram)
    #for i1 in range(100000):
    #    word = tm1.babble()
    #dump_histogram(tm1._actual_histogram)
    #sh1 = scale_histogram_to_per_million(tm1._target_histogram)
    #sh2 = scale_histogram_to_per_million(tm1._actual_histogram)
    #ratios = array.array('d', (target/actual if actual > 0 else 0 for target, actual in zip(sh1, sh2)))
    #maximum = max(value for value in ratios)
    #for i1 in range(len(ratios)):
    #    ratios[i1] = ratios[i1] / maximum
    #dump_histogram(ratios)
    tm3 = FilteredBabbler(TwoLetterTerminal())
    tm3.add_filter(BabblerFilterNotTooShort())
    tm3.add_filter(BabblerFilterDontUseThese(girls))
    tm4 = BabblerFilterMatchHistogram()
    tm3.add_filter(tm4)
    tm3.process(girls)
    dump_histogram(tm3._makes_words._target_histogram)
    #for i1 in range(100000):
    #    word = tm3.babble()
    #dump_histogram(tm4._actual_histogram)
    # Determine probabilities of keeping a babble based on the length (histogram matching)
    #t1 = copy.copy(tm3._makes_words._target_histogram)
    #t1[1] = 0
    #dump_histogram(t1)
    #sh1 = scale_histogram_to_per_million(t1)
    #sh2 = scale_histogram_to_per_million(tm4._actual_histogram)
    #ratios = array.array('d', (target/actual if actual > 0 else 0 for target, actual in zip(sh1, sh2)))
    #maximum = max(value for value in ratios)
    #probabilities = array.array('d', (ratio/maximum for ratio in ratios))
    #dump_probabilities(probabilities)
    #tm4._chance_to_keep = probabilities
    #for i1 in range(len(tm4._actual_histogram)):
    #    tm4._actual_histogram[i1] = 0
    for i1 in range(100000):
        word = tm3.babble()
    dump_histogram(tm4._actual_histogram)
    for i1 in range(20):
        word = tm3.babble()
        logger.info("{}, {}".format(word, word in girls))
    logger.info("------------------------------------------------------------")


def get_common_name(row):
    for item in row:
        if item.startswith('CN='):
            return item[3:]
    return None


def X_test_002(caplog):
    caplog.set_level(logging.INFO)
    load_these = Path('./First Names')
    logger.info(list(load_these.glob('*.txt')))
    load_these = list(Path('./First Names').glob('*.txt')) + \
            [Path('first_names.txt')]
    logger.info(load_these)

def x_test_001(caplog):
    caplog.set_level(logging.INFO)
    #load_this = 'first_names.txt'
    load_these = list(Path('./First Names').glob('*.txt')) + \
            [Path('first_names.txt')]
    tm1 = TwoLetterTerminal1()
    total = 0
    success = 0
    for load_this in load_these:
        with load_this.open() as inf:
            reader = csv.reader(inf)
            for row in reader:
                if len(row) > 0:
                    if len(row) >= 3:
                        increment = int(row[2])
                    else:
                        increment = 1
                    if tm1.process_words(row[0], increment):
                        success += 1
                    else:
                        logger.info('Skipped: "{}"'.format(row[0]))
                    total += 1
            #for line in inf:
            #    naked = line.strip()
            #    if tm1.process_words(naked):
            #        success += 1
            #    else:
            #        logger.info('Skipped: "{}"'.format(naked))
            #    total += 1
    logger.info('{} / {} = {}%'.format(success, total, 100.0*success/total))
    for i1 in range(100):
        word, status = tm1.babble()
        logger.info('{}, {}'.format(word, status))

"""
p1 = pickle.dumps(tm1, protocol=pickle.HIGHEST_PROTOCOL)
tm2 = pickle.loads(p1)

import csv
f = open('Names_2010Census.csv')
r = csv.DictReader(f)
r.fieldnames
count = 10
for d in r:
    count -= 1
    if count <= 0:
        break
    print(d)

r = csv.reader(f)

line = f.readline()

f.close()

import test_babble

girls, boys = test_babble.get_first_name_sets()

tm1 = test_babble.TwoLetterTerminal()
tm1.process_words(girls)


conflict = 0
total = 0
for i1 in range(1000000):
    word = tm1.babble()
    status = word in girls
    if status:
        tm1.punish(word)
        conflict += 1
    total += 1

print(conflict, total, 100.0*conflict/total)


conflict = 0
total = 0
seen = set()
for i1 in range(1000000):
    word = tm1.babble()
    if word in seen:
        conflict += 1
    else:
        seen.add(word)
    total += 1

print(conflict, total, 100.0*conflict/total)

"""
