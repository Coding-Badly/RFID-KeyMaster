"""=============================================================================

  MemberDataCacher for RFID-KeyMaster.  MemberDataCacher is responsible for
  maintaining a cache of the most recent member data.  If cached data is
  available on startup MemberDataCacher loads it and publishes it.  When fresh
  member data is available it is saved to disk.  Anything interested in member
  data should subscribe to both Signals.CACHED_DATA and Signals.FRESH_DATA.
  Obviously FRESH_DATA should be favoured.

  ----------------------------------------------------------------------------

  Copyright 2019 Mike Cole (aka @Draco, MikeColeGuru)
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
from drivers import Signals
from drivers.DriverBase import DriverBase
import gzip
import json
import logging
import pathlib
import pickle
from utils import get_cache_path
from utils.twophaser import two_phase_open

logger = logging.getLogger(__name__)

class RetryLoad(Exception):
    pass

class MemberDataCacheFile():
    def __init__(self, suffix):
        super().__init__()
        self._path = get_cache_path() / ('MemberData' + suffix)
    def dump(self, data):
        pass
    def load(self):
        return None
    def get_path(self):
        return self._path

class MemberDataCacheFileAsJson(MemberDataCacheFile):
    def __init__(self):
        super().__init__('.json')
    def dump(self, data):
        with two_phase_open(self._path, 'wt') as ous:
            json.dump(data, ous)
    def load(self):
        try:
            with two_phase_open(self._path, 'rt') as f:
                data = json.load(f)
        except json.decoder.JSONDecodeError:
            self._path.unlink()
            raise RetryLoad()
        return data

class MemberDataCacheFileAsPickleGzip(MemberDataCacheFile):
    def __init__(self):
        super().__init__('.pickle.gz')
    def dump(self, data):
        with two_phase_open(self._path, 'wb') as ous:
            with gzip.open(ous, 'wb') as ous:
                pickle.dump(data, ous, protocol=pickle.HIGHEST_PROTOCOL)
    def load(self):
        try:
            with two_phase_open(self._path, 'rb') as ins:
                with gzip.open(ins, 'rb') as ins:
                    data = pickle.load(ins)
        except pickle.PickleError:
            self._path.unlink()
            raise RetryLoad()
        return data

class MemberDataCacher(DriverBase):
    _events_ = [Signals.CACHED_DATA]
    def _after_init(self):
        super()._after_init()
        # rmv? self._file_manager = MemberDataCacheFileAsJson()
        self._file_manager = MemberDataCacheFileAsPickleGzip()
        # rmv self._path = get_cache_path() / 'MemberData.json'
    def setup(self):
        super().setup()
        self.subscribe(None, Signals.FRESH_DATA, self.receive_fresh_data)
    def startup(self):
        super().startup()
        self.open_for_business()
        keep_trying = True
        while keep_trying:
            keep_trying = False
            try:
                data = self._file_manager.load()
                self.publish(Signals.CACHED_DATA, data)
                logger.info('Cached member data published.')
            except FileNotFoundError:
                logger.warning('Cached member data not available.')
            except RetryLoad:
                logger.error('Cached member data is corrupt.')
                keep_trying = True
            # rmv try:
            # rmv     with two_phase_open(self._path, 'rt') as f:
            # rmv         data = json.load(f)
            # rmv     self.publish(Signals.CACHED_DATA, data)
            # rmv     logger.info('Cached member data published.')
            # rmv except FileNotFoundError:
            # rmv     logger.warning('Cached member data not available.')
            # rmv # fix: https://docs.python.org/3/library/pickle.html#pickle.UnpicklingError
            # rmv # fix: pickle.PickleError
            # rmv # fix: AttributeError, EOFError, ImportError, IndexError
            # rmv # fix: Exception
            # rmv except json.decoder.JSONDecodeError:
            # rmv     logger.error('Cached member data is corrupt.')
            # rmv     self._path.unlink()
            # rmv     keep_trying = True
    def receive_fresh_data(self, data):
        self._file_manager.dump(data)
        # rmv with two_phase_open(self._path, 'wt') as f:
        # rmv     json.dump(data, f)
    def get_path(self):
        return self._file_manager.get_path()

