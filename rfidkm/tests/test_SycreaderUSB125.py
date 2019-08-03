"""=============================================================================

  pytest for SycreaderUSB125.

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
import platform
import pytest

import rfidkm.tests.exercise as exercise

if not exercise.rfid_readers:
    pytest.skip("skipping RFID reader tests", allow_module_level=True)

if platform.system() == 'Windows':
    pytest.skip("skipping tests that will not run on Windows", allow_module_level=True)

import logging

from rfidkm.drivers.signals import Signals, DriverSignals, KeyMasterSignals
from rfidkm.drivers.DriverBase import DriverBase, DriverGroup
from rfidkm.drivers.RFID.SycreaderUSB125 import SycreaderUSB125
from rfidkm.drivers.RFID.SycreaderUSB125 import find_an_saor_rfid_readers

logger = logging.getLogger(__name__)

class TagBase():
    def __init__(self, color):
        self._color = color
    def action(self, target):
        return ''

class NormalTag(TagBase):
    pass

class StopTag(TagBase):
    def action(self, target):
        super().action(target)
        target.publish(DriverSignals.STOP_NOW)
        return 'stop'

class SimplePrintTagController(DriverBase):
    _events_ = [DriverSignals.STOP_NOW]
    def setup(self):
        super().setup()
        self._no_tag = NormalTag('Unknown')
        self._tags = dict()
        self._tags['0004134263'] = NormalTag('Black')
        self._tags['0002864796'] = NormalTag('Blue')
        self._tags['0005675589'] = NormalTag('Green')
        self._tags['0008683072'] = NormalTag('Purple')
        self._tags['0006276739'] = NormalTag('Red')
        self._tags['0007062381'] = NormalTag('Pink')
        self._tags['0016182332'] = NormalTag('Yellow')
        self._tags['0015261977'] = StopTag('Death of Rats')
        self._reader = int(self.config.get('reader', 0))
        self.subscribe(None, KeyMasterSignals.SWIPE_10, self.receive_swipe_10, determines_start_order=False)
    def startup(self):
        super().startup()
        self.open_for_business()
    # self.publish(KeyMasterSignals.SWIPE_10, self._parser.timestamp, self._parser.rfid)
    def receive_swipe_10(self, timestamp, rfid):
        tag = self._tags.get(rfid, self._no_tag)
        logger.info('#{}: {} {} {} - {}'.format(self._reader, timestamp, rfid, tag._color, tag.action(self)))

def create_rfid_reader(config):
    root = DriverGroup()
    jk1 = root.add(SycreaderUSB125(config))
    tm1 = root.add(SimplePrintTagController(config))
    return root

def run_root(root):
    root.setup()
    root.start()
    root.join()
    root.teardown()

def run_rfid_reader(config):
    root = create_rfid_reader(config)
    run_root(root)

def run_all_readers_at_once(which):
    root = DriverGroup()
    for i1 in range(len(find_an_saor_rfid_readers())):
        config = {"driver": "SycreaderUSB125"}
        if "reader" in which:
            config["reader"] = i1
        if "group_number" in which:
            config["group_number"] = i1
        root.add(create_rfid_reader(config))
    logger.info('Scan away...')
    run_root(root)

def test_all_readers_at_once(caplog, exercise_rfid_readers):
    if exercise_rfid_readers:
        caplog.set_level(logging.INFO)
        run_all_readers_at_once(frozenset({"reader", "group_number"}))
        run_all_readers_at_once(frozenset({"reader"}))
        run_all_readers_at_once(frozenset({"group_number"}))

