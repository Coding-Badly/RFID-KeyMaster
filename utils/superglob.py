"""=============================================================================

  SuperGlobAndOpen for RFID-KeyMaster.  SuperGlobAndOpen provides a multi-root
  zip-file-friendly glob with the expection that each file will be opened as
  text for reading.  The intended purpose is loading example data that is used
  to prepare test data.
  
  ----------------------------------------------------------------------------

    # Create an instance
    t1 = SuperGlobAndOpen()
    # Add root paths which can be simple files, zip files, or wildcards
    t1.add(pathlib.Path('./First Names/names.zip'))
    t1.add(pathlib.Path('first_names.txt'))
    # Each item returned is a "file opener" that returns a file-like object
    last10 = collections.deque([], 10)
    for opener in t1:
        if opener.name.suffix.lower() == '.txt':
            with opener.open() as inf:
                reader = csv.reader(inf)
                for row in reader:
                    last10.append(row)
    while last10:
        row = last10.popleft()
        logger.info(row)

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
import collections
import io
import logging
import os
import pathlib
import pyzipper

logger = logging.getLogger(__name__)

class SuperGlobIterator():
    def __init__(self, list_of_paths):
        self._list_of_paths = list_of_paths
        self._index = 0
    def _get_next(self):
        while True:
            try:
                path_entry = self._list_of_paths[self._index]
                try:
                    path = next(path_entry)
                    path_supports_next = True
                except StopIteration:
                    path = None
                    path_supports_next = True
                except TypeError:
                    path = path_entry
                    path_supports_next = False
            except IndexError:
                raise StopIteration
            if path:
                if path_supports_next:
                    return path
                else:
                    self._index += 1
                    return path
            else:
                self._index += 1
    def __next__(self):
        return self._get_next()

class SuperGlob():
    def __init__(self, list_of_paths=None):
        self._list_of_paths = list() if list_of_paths is None else list_of_paths
        self._current_iter = None
    def __iter__(self):
        return SuperGlobIterator(self._list_of_paths)
    def add(self, path):
        self._list_of_paths.append(path)


class GenericOpener():
    def __init__(self):
        self._close_me = collections.deque()
    def _append(self, close_me):
        self._close_me.append(close_me)
        return close_me
    def __exit__(self, exc_type, exc_value, traceback):
        while self._close_me:
            self._close_me.pop().close()
        return False
    def open(self):
        return self
    @property
    def name(self):
        return ''
    @property
    def path(self):
        return pathlib.Path('.')

class TextFileOpener(GenericOpener):
    def __init__(self, path):
        super().__init__()
        self._path = path
    def __enter__(self):
        return self._append(self._path.open('rt'))
    @property
    def name(self):
        return pathlib.Path(self._path.name)
    @property
    def path(self):
        return self._path

class ZipFileOpener(GenericOpener):
    def __init__(self, path, name, password, empty_if_bad_password):
        super().__init__()
        self._path = path
        self._name = name
        self._password = password
        self._empty_if_bad_password = empty_if_bad_password
    def __enter__(self):
        zip = self._append(pyzipper.AESZipFile(self._path))
        try:
            stream = zip.open(self._name, 'r', self._password)
        except RuntimeError as exc:
            if self._empty_if_bad_password and (str(exc).upper().find('PASSWORD') >= 0):
                stream = io.BytesIO()
            else:
                raise
        inf = self._append(stream)
        wrapper = self._append(io.TextIOWrapper(inf))
        return wrapper
    @property
    def name(self):
        return pathlib.Path(self._name)
    @property
    def path(self):
        return self._path


ENVIRONMENT_VARIABLE_PREFIX = 'SUPERGLOB_PASSWORD_'

def clean_stem_to_simple_environment_variable(stem):
    rv = ''
    for ch in stem:
        if ch >= 'A' and ch <= 'Z':
            rv += ch
        elif ch >= 'a' and ch <= 'z':
            rv += chr(ord(ch)-ord('a')+ord('A'))
        else:
            rv += '_'
    return rv

class SuperGlobAndOpenIterator(SuperGlobIterator):
    def __init__(self, parent):
        super().__init__(parent._list_of_paths)
        self._skip_if_not_exists = parent._skip_if_not_exists
        self._empty_if_bad_password = parent._empty_if_bad_password
        self._zip = None
        self._names = None
    def __next__(self):
        while True:
            if self._names:
                name = self._names.popleft()
                e1 = ENVIRONMENT_VARIABLE_PREFIX + clean_stem_to_simple_environment_variable(str(self._zip.stem))
                n1 = clean_stem_to_simple_environment_variable(pathlib.Path(name).stem)
                e2 = e1 + '_' + n1
                p1 = os.getenv(e2, None) or os.getenv(e1, None)
                if p1:
                    p1 = p1.encode('utf-8')
                return ZipFileOpener(self._zip, name, p1, self._empty_if_bad_password)
            else:
                path = self._get_next()
                if not path.exists() and self._skip_if_not_exists:
                    continue
                if path.suffix == '.zip':
                    self._zip = path
                    with pyzipper.AESZipFile(path) as zip:
                        self._names = collections.deque(zip.namelist())
                else:
                    return TextFileOpener(path)

class SuperGlobAndOpen(SuperGlob):
    def __init__(self, list_of_paths=None, skip_if_not_exists=False, empty_if_bad_password=False):
        super().__init__(list_of_paths)
        self._skip_if_not_exists = skip_if_not_exists
        self._empty_if_bad_password = empty_if_bad_password
    def __iter__(self):
        return SuperGlobAndOpenIterator(self)

