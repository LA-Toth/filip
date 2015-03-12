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
        self.__entries[name] = entry

    def remove(self, name: str):
        del self.__entries[name]

    def has(self, name: str):
        return name in self.__entries

    def get(self, name: str):
        return self.__entries[name]

    def __getitem__(self, item):
        return self.__entries[item]

    def __len__(self):
        return len(self.__entries)


class InMemoryFilesystem:

    def __init__(self):
        self.__tree = _Directory()
        self.__current_directory = []

    def __normalize_and_split_path(self, path):
        if path.startswith(os.path.sep):
            abs_path_list = os.path.normpath(path).split(os.path.sep)[1:]
        else:
            normalized_abs_path = os.path.normpath(os.path.sep.join(self.__current_directory) + os.path.sep + path)
            abs_path_list = normalized_abs_path.split(os.path.sep)

        return [p for p in abs_path_list if p]

    def makedirs(self, path: str):
        abs_path = self.__normalize_and_split_path(path)
        if len(abs_path) == 0:
            raise FileExistsError(os.path.sep)

        current = self.__tree
        for entry in abs_path[:-1]:
            if not current.has(entry):
                current.add(entry, _Directory())
            current = current[entry]

        name = abs_path[-1]
        if current.has(name):
            raise FileExistsError(path)
        current.add(name, _Directory())

    def remove_directory(self, path: str):
        if not self.exists(path):
            raise FileNotFoundError(path)

        abs_path = self.__normalize_and_split_path(path)
        current = self.__tree

        for entry in abs_path[:-1]:
            current = current[entry]

        name = abs_path[-1]
        if len(current[name]):
            raise OSError(path)
        current.remove(name)

    def exists(self, path: str):
        abs_path = self.__normalize_and_split_path(path)
        current = self.__tree

        for entry in abs_path:
            if not current.has(entry):
                return False

            current = current[entry]

        return True

    def get_current_directory(self):
        return os.path.sep + os.path.sep.join(self.__current_directory)

    def set_current_directory(self, path: str):
        if not self.exists(path):
            raise FileNotFoundError(path)
        self.__current_directory = self.__normalize_and_split_path(path)
