# Copyright (c) 2015 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import os.path
import unittest

from filip.memory.filesystem import InMemoryFilesystem


class TestFilesystem(unittest.TestCase):

    def setUp(self):
        self.fs = InMemoryFilesystem()

    def test_that_single_directory_can_be_added(self):
        self.assertFalse(self.fs.exists('plum'))
        self.fs.makedirs('plum')
        self.assertTrue(self.fs.exists('plum'))

    def test_that_subdirectories_can_be_added_in_one_step(self):
        self.fs.makedirs('apple')
        self.fs.makedirs(os.path.join('apple', 'pine', 'plum'))
        self.assertTrue(self.fs.exists(os.path.join('apple', 'pine', 'plum')))
        self.assertTrue(self.fs.exists(os.path.join('', 'apple', 'pine')))
        self.assertTrue(self.fs.exists('apple'))

    def test_that_a_directory_cannot_be_created_twice(self):
        self.fs.makedirs('apple')
        self.assertRaises(FileExistsError, self.fs.makedirs, 'apple')
