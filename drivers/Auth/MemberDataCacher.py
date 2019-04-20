"""=============================================================================

  MemberDataCacher for RFID-KeyMaster.  MemberDataCacher is responsible for
  maintaining a cache of the most recent member data.  If cached data is
  available on startup MemberDataCacher loads it and publishes it.  When fresh
  member data is available it is saved to disk.  Anything interested in member
  data should subscribe to both MemberDataCacher.CACHED_DATA and
  MemberDataFreshener.FRESH_DATA.  Obviously FRESH_DATA should be favoured.

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
from drivers.DriverBase import DriverBase
import json
import logging
import pathlib
from utils.twophaser import two_phase_open

logger = logging.getLogger(__name__)

class MemberDataCacher(DriverBase):
    CACHED_DATA = 'cached_member_data'
    _events_ = [CACHED_DATA]
    MEMBER_DATA_FILENAME = 'MemberData.json'
    def setup(self):
        super().setup()
        self.subscribe(None, 'fresh_member_data', self.receive_fresh_data)
    def startup(self):
        super().startup()
        self.open_for_business()
        keep_trying = True
        while keep_trying:
            keep_trying = False
            try:
                with two_phase_open(MemberDataCacher.MEMBER_DATA_FILENAME, 'rt') as f:
                    data = json.load(f)
                self.publish(MemberDataCacher.CACHED_DATA, data)
                logger.info('Cached member data published.')
            except FileNotFoundError:
                logger.warning('Cached member data not available.')
            except json.decoder.JSONDecodeError:
                logger.error('Cached member data is corrupt.')
                primary_path = pathlib.Path(MemberDataCacher.MEMBER_DATA_FILENAME)
                primary_path.unlink()
                keep_trying = True
    def receive_fresh_data(self, data):
        with two_phase_open(MemberDataCacher.MEMBER_DATA_FILENAME, 'wt') as f:
            json.dump(data, f)

