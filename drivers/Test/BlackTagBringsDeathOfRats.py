"""=============================================================================

  BlackTagBringsDeathOfRats for RFID-KeyMaster testing.
  BlackTagBringsDeathOfRats stops all threads when the black RFID tag is
  swiped.

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
from drivers.signals import KeyMasterSignals
from drivers.DriverBase import DriverBase, DeathOfRats

class BlackTagBringsDeathOfRats(DeathOfRats):
    def setup(self):
        super().setup()
        self._black_tag = self.config.get('black_tag', '0004134263')
        self.subscribe(None, KeyMasterSignals.SWIPE_10, self.receive_swipe_10, determines_start_order=False)
    def receive_swipe_10(self, timestamp, rfid):
        if rfid == self._black_tag:
            self._stop_now()
