"""=============================================================================

  MemberDataFreshener for RFID-KeyMaster.  MemberDataFreshener is responsible
  for getting fresh member / group data from a server.  The connection details
  (e.g. the server name / address) are expected to be passed during
  construction in the config parameter.  The data returned from the server is
  expected to be JSON formatted...

      {
        "0079313829":
        {
          "user":
          {
            "fullName":"Brian Cook",
            "groups":["Machine Shop Sherline Lathe","Woodshop Basics","3D Printer Form2","CA DyeSub Printer","Automotive 102 (Lift Training)","Members"],
            "username":"Coding-Badly"
          }
        },
        "0752874821":...
      }

  ETag is used to minimize network traffic.  The server is expected to return
  a 304 Not Modified if the member data has not changed.  When fresh data is
  available this driver publishes the data as a fresh_member_data event.

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
import requests

logger = logging.getLogger(__name__)

def fix_etag(headers):
    raw = headers.get('ETag', None)
    if raw is None:
        return None
    content_encoding = headers.get('Content-Encoding', None)
    if content_encoding is None:
        return raw
    no_quotes = raw.strip('"')
    if no_quotes.endswith(content_encoding):
        no_quotes = no_quotes[:-len(content_encoding)-1]
    return '"' + no_quotes + '"'

class MemberDataFreshener(DriverBase):
    FRESH_DATA = 'fresh_member_data'
    _events_ = [FRESH_DATA]
    def poll_for_fresh_data(self):
        with self._session as s:
          response = s.get(self._remote_cache_url, headers=self._request_headers)  # fix: verify=False
        if response.status_code == requests.codes.ok:
            try:
                data = response.json()
                self.publish(MemberDataFreshener.FRESH_DATA, data)
                logger.info('Fresh member data published.')
                etag = fix_etag(response.headers)
                logger.info('etag = %s.', etag)
                self._request_headers['If-None-Match'] = etag
            except json.decoder.JSONDecodeError as exc:
                logger.exception('Unable to parse member data.')
        elif response.status_code == requests.codes.not_modified:
            logger.info('Member data has not changed since the last publication.')
            pass
        else:
            response.raise_for_status()
    def setup(self):
        super().setup()
        logger.info('MemberDataFreshener.setup...')
        self._remote_cache_url = 'https://www.rowdydogsoftware.com/TKRn2uZNBSCSBcTUPRFPhHBL/adcache.json'
        self._request_headers = {}
        self._session = requests.Session()
        logger.info('MemberDataFreshener.setup fini.')
    def startup(self):
        super().startup()
        # fix self.call_every(60.0, self.poll_for_fresh_data, fire_now=True)
        self.call_every(2.5, self.poll_for_fresh_data, fire_now=True) # rmv
        self.open_for_business()
    def teardown(self):
        self._session.close()
        self._session = None
        self._request_headers = None
        self._remote_cache_url = None