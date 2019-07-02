"""=============================================================================

  insulation_linux for RFID-KeyMaster.  insulation_linux provides insulation
  from the Linux operating system.  While Python is highly  portable it is not
  perfect.  The location of files is a good example.  RFID-KeyMaster needs to
  cache data.  The application directory is not an appropriate location.  Each
  operating system has a reasonable location for such files but those
  locations are radically different.  The purpose of this module (and its
  sibling insulation_windows) is provide a consistent view of the world
  despite the operating system differences.

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
import pathlib

CACHE_PATH = None

def get_cache_path():
    """Return a Path to the cache directory for the RFID-KeyMaster application.

    This function also ensures the cache directory exists and has reasonable
    permissions.
    """
    # pylint: disable=global-statement
    global CACHE_PATH
    if CACHE_PATH is None:
        CACHE_PATH = pathlib.Path('/var/cache/Dallas Makerspace/RFID-KeyMaster')
        CACHE_PATH.mkdir(mode=0o755, parents=True, exist_ok=True)
    return CACHE_PATH
