"""=============================================================================

  SecurityContext for RFID-KeyMaster.  SecurityContext binds Permissions,
  Groups, and Users in a package that somewhat resembles the Django contrib
  security model.  The goal is to provide something that works and will be
  familiar.

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
from collections.abc import Mapping

class Permission():
    def __init__(self, codename, name=None):
        self._codename = codename
        self._name = name
    def __hash__(self):
        return hash((self._codename))
    def __eq__(self, other):
        return isinstance(other, Permission) and (self._codename == other._codename)
    def __repr__(self):
        return 'Permission({!r}, {!r})'.format(self._codename, self._name)
    def _get_init_tuple(self):
        return (self._codename, self._name)
    # codename = 'power'
    # name = 'User can enable power for the tool.'
    # content_type = None 
    # app_label = 'KeyMaster'

class Group():
    def __init__(self, name):
        self._name = name
        self._permissions = None
    def __hash__(self):
        return hash((self._name))
    def __eq__(self, other):
        return isinstance(other, Group) and (self._name == other.name)
    def __repr__(self):
        return 'Group({!r})'.format(self._name)
    def _get_init_tuple(self):
        if self._permissions:
            return (self._name, [i1._get_init_tuple() for i1 in self._permissions])
        else:
            return (self._name,)
    @property
    def name(self):
        return self._name
    # name
    # permissions

def repr_init_list(dict_to_use, indent):
    rv = '['
    lft = ''
    prefix = '\n' + (' ' * indent)
    for value in dict_to_use.values():
        rv += lft + prefix + repr(value._get_init_tuple())
        lft = ','
    rv += ']'
    return rv

class SecurityContext():
    def __init__(self, permissions=None, groups=None):
        self._permissions = dict()
        self._groups = dict()
        if permissions:
            _ = self._prepare_permissions_to_use(permissions)
        if isinstance(groups, Mapping):
            for rover in groups:
                self.add_group(rover, groups[rover])
        elif isinstance(groups, str):
            self.add_group(groups, None)
        elif isinstance(groups, tuple):
            if isinstance(groups[0], tuple):
                self._iterate_add_groups(groups)
            else:
                self.add_group(groups[0], groups[1])
        elif groups:
            self._iterate_add_groups(groups)
    def __eq__(self, other):
        if isinstance(other, SecurityContext) \
                and (self._permissions == other._permissions) \
                and (self._groups == other._groups):
            for key, g1 in self._groups.items():
                g2 = other._groups[key]
                if g1._permissions != g2._permissions:
                    return False
            return True
        else:
            return False
    def __repr__(self):
        p1 = [i1._get_init_tuple() for i1 in self._permissions.values()]
        return 'SecurityContext(\n   permissions={!s},\n   groups={!s})'. \
            format(repr_init_list(self._permissions,8), repr_init_list(self._groups, 8))
    def _iterate_add_permissions(self, rv, permissions):
        for rover in permissions:
            if isinstance(rover, tuple) and (len(rover) > 1):
                rv.add(self.add_permission(rover[0], rover[1]))
            else:
                rv.add(self.add_permission(rover, None))
    def _iterate_add_groups(self, groups):
        for rover in groups:
            if isinstance(rover, tuple) and (len(rover) > 1):
                self.add_group(rover[0], rover[1])
            else:
                self.add_group(rover, None)
    def _prepare_permissions_to_use(self, permissions):
        rv = set()
        if isinstance(permissions, Mapping):
            for rover in permissions:
                rv.add(self.add_permission(rover, permissions[rover]))
        elif isinstance(permissions, str):
            rv.add(self.add_permission(permissions, None))
        elif isinstance(permissions, tuple):
            if isinstance(permissions[0], tuple):
                self._iterate_add_permissions(rv, permissions)
            else:
                rv.add(self.add_permission(permissions[0], permissions[1]))
        elif permissions:
            self._iterate_add_permissions(rv, permissions)
        return rv
    def add_permission(self, codename, name):
        rv = self._permissions.get(codename, None)
        if not rv:
            rv = Permission(codename, name)
            rv._context = self
            self._permissions[codename] = rv
        #else:
        #    # Update name?
        #    # Validate name?
        #    # Ignore name?
        #    pass
        return rv
    def add_group(self, name, permissions=None):
        rv = self._groups.get(name, None)
        if rv:
            if permissions:
                rv._permissions = self._prepare_permissions_to_use(permissions)
        else:
            rv = Group(name)
            rv._context = self
            rv._permissions = self._prepare_permissions_to_use(permissions)
            self._groups[name] = rv
        return rv

