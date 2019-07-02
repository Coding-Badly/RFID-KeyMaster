"""=============================================================================

  Preserve a precious file during a test.

  ----------------------------------------------------------------------------

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
import enum
import pathlib
import uuid

class PreservedFileAction(enum.Enum):
    """Action needed to restore a preserved file.
    """
    NOTHING = 1
    RENAME = 2
    DELETE = 3

class PreservedFile():
    """Preserve one precious file during a test.
    """
    def __init__(self, path):
        self._original = path if isinstance(path, pathlib.Path) else pathlib.Path(path)
        self._preserved = None
        self._action = PreservedFileAction.NOTHING
    def __hash__(self):
        return hash(self._original)
    @staticmethod
    def _get_other_to_compare(other):
        # pylint: disable=no-else-return
        # pylint: disable=protected-access
        if isinstance(other, PreservedFile):
            return other._original
        elif isinstance(other, pathlib.Path):
            return other
        else:
            return other
    def __lt__(self, other):
        return self._original.__lt__(PreservedFile._get_other_to_compare(other))
    def __le__(self, other):
        return self._original.__le__(PreservedFile._get_other_to_compare(other))
    def __eq__(self, other):
        return self._original.__eq__(PreservedFile._get_other_to_compare(other))
    def __ne__(self, other):
        return self._original.__ne__(PreservedFile._get_other_to_compare(other))
    def __gt__(self, other):
        return self._original.__gt__(PreservedFile._get_other_to_compare(other))
    def __ge__(self, other):
        return self._original.__ge__(PreservedFile._get_other_to_compare(other))
    def preserve_it(self, prefix):
        """If the file exists rename it otherwise remember to delete it.
        """
        if self._action == PreservedFileAction.NOTHING:
            self._preserved = self._original.parent / (prefix + self._original.name)
            if self._original.exists():
                self._original.rename(self._preserved)
                self._action = PreservedFileAction.RENAME
            else:
                self._action = PreservedFileAction.DELETE
    def restore_it(self):
        """If the existed then restore it otherwise delete it
        """
        if self._action == PreservedFileAction.RENAME:
            if self._original.exists():
                self._original.unlink()
            self._preserved.rename(self._original)
        elif self._action == PreservedFileAction.DELETE:
            if self._original.exists():
                self._original.unlink()
            if self._preserved.exists():
                self._preserved.unlink()
        self._action = PreservedFileAction.NOTHING

class FilePreserver():
    """Context manager the preserves precious files during a test.
    """
    def __init__(self, *args):
        self._prefix = uuid.uuid4().hex + '-'
        self._preserve_these = set()
        for path in args:
            self.preserve_this(path)
    def preserve_this(self, path):
        """Add another file to be preserved.
        """
        self._preserve_these.add(PreservedFile(path))
        return self
    def __iadd__(self, other):
        # fix? if other is a FilePreserver then copy its list to ours?
        self.preserve_this(other)
        return self
    def __enter__(self):
        for path in self._preserve_these:
            path.preserve_it(self._prefix)
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        for path in self._preserve_these:
            path.restore_it()
        return False
