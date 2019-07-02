"""=============================================================================

  insulation_windows for RFID-KeyMaster.  insulation_windows provides
  insulation from the Windows operating system.  While Python is highly
  portable it is not perfect.  The location of files is a good example.
  RFID-KeyMaster needs to cache data.  The application directory is not an
  appropriate location.  Each operating system has a reasonable location for
  such files but those locations are radically different.  The purpose of
  this module (and its sibling insulation_linux) is provide a consistent view
  of the world despite the operating system differences.

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
# pylint: disable=no-name-in-module
# pylint: disable=import-error

import pathlib
from win32com.shell import shell, shellcon

CSIDL_FLAG_CREATE = 0x8000

def rd_get_folder_path(csidl, append_this, options):
    """Return a standard Windows Path optionally appending a subdirectory name.
    """
    # pylint: disable=unused-argument
    rv = pathlib.Path(shell.SHGetFolderPath(0, csidl | CSIDL_FLAG_CREATE, None, 0))
    if csidl in [shellcon.CSIDL_APPDATA,
                 shellcon.CSIDL_COMMON_APPDATA,
                 shellcon.CSIDL_COMMON_DOCUMENTS]:
        rv = rv / 'Dallas Makerspace'
    elif csidl in [shellcon.CSIDL_PERSONAL,
                   shellcon.CSIDL_DESKTOPDIRECTORY,
                   shellcon.CSIDL_COMMON_DESKTOPDIRECTORY,
                   shellcon.CSIDL_STARTMENU,
                   shellcon.CSIDL_COMMON_STARTMENU]:
        pass
    else:
        raise Exception(
            'Unsupported CSIDL ({}) passed to rd_get_folder_path'.format(csidl))
    if append_this:
        rv = rv / append_this
    # Note: Options is currently ignored.
    return rv

CACHE_PATH = None

def get_cache_path():
    """Return a Path to the cache directory for the RFID-KeyMaster application.

    This function also ensures the cache directory exists and has reasonable
    permissions.
    """
    # pylint: disable=global-statement
    global CACHE_PATH
    if CACHE_PATH is None:
        CACHE_PATH = rd_get_folder_path(shellcon.CSIDL_COMMON_APPDATA, 'RFID-KeyMaster', None)
        CACHE_PATH = CACHE_PATH / 'Cache'
        CACHE_PATH.mkdir(mode=0o755, parents=True, exist_ok=True)
    return CACHE_PATH
