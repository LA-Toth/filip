# Copyright (c) 2015 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import os.path


class _Entry:
    pass


class _Directory(_Entry):
    def __init__(self):
        super().__init__()
        self.__entries = dict()

    def add(self, name: str, entry: _Entry):
        if name in self.__entries:
            raise FileExistsError()
        self.__entries[name] = entry

    def has(self, name: str):
        return name in self.__entries

    def get(self, name: str):
        return self.__entries[name]

    def __getitem__(self, item):
        return self.__entries[item]


class InMemoryFilesystem:

    def __init__(self):
        self.__tree = _Directory()

    def makedirs(self, path: str):
        path = path.split(os.path.sep)
        current = self.__tree
        for entry in path[:-1]:
            if not entry:
                continue
            if not current.has(entry):
                current.add(entry, _Directory())
            current = current[entry]

        current.add(path[-1], _Directory())

    def exists(self, path: str):
        path = path.split(os.path.sep)
        current = self.__tree

        for entry in path:
            if not entry:
                continue

            if not current.has(entry):
                return False

            current = current[entry]

        return True
