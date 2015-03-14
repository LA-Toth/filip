# Copyright (c) 2015 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import os.path
import unittest

from filip.memory.filesystem import InMemoryFilesystem


class FileSystemTest(unittest.TestCase):
    def setUp(self):
        self.fs = InMemoryFilesystem()

    def assertExist(self, path: str):
        self.assertTrue(self.fs.exists(path), msg='The filesystem entry is missing, it should exist')

    def assertNotExist(self, path: str):
        self.assertFalse(self.fs.exists(path), msg='The filesystem entry exists, it should be missing')


class TestFilesystemsDirectoryRelatedMethods(FileSystemTest):

    def test_that_root_directory_exists(self):
        self.fs.exists(os.path.sep)

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

    def test_that_paths_are_normalized(self):
        self.fs.makedirs((os.path.sep * 4) + 'apple' + (os.path.sep * 3) + 'pine')
        self.assertTrue(self.fs.exists((os.path.sep * 40) + 'apple' + (os.path.sep * 40) + 'pine'))
        self.assertTrue(self.fs.exists(os.path.join('apple', 'pine')))

    def test_that_a_directory_cannot_be_created_twice(self):
        self.fs.makedirs('apple')
        self.assertRaises(FileExistsError, self.fs.makedirs, 'apple')

    def test_that_root_directory_cannot_be_recreated(self):
        self.assertRaises(FileExistsError, self.fs.makedirs, os.path.sep)

    def test_that_default_directory_is_root(self):
        self.assertIn(self.fs.get_current_directory(), (os.path.sep, ''))

    def test_that_current_directory_cannot_be_changed_to_nonexistent(self):
        self.assertRaises(FileNotFoundError, self.fs.set_current_directory, 'nonexistent')

    def test_that_current_directory_can_be_changed(self):
        self.fs.makedirs(os.path.join('apple', 'pine'))
        self.fs.set_current_directory(os.path.join('apple', 'pine'))
        self.assertEqual(os.path.sep.join(['', 'apple', 'pine']), self.fs.get_current_directory())

    def test_that_exists_method_is_affected_by_current_directory(self):
        self.fs.makedirs(os.path.sep + 'a_dir')
        self.fs.set_current_directory(os.path.sep + 'a_dir')
        self.assertFalse(self.fs.exists('a_dir'))
        self.assertTrue(self.fs.exists(os.path.join('..', 'a_dir')))
        self.assertTrue(self.fs.exists(os.path.sep + 'a_dir'))

    def test_that_creating_directory_with_relative_path_is_based_on_current_directory(self):
        self.fs.makedirs('mydirectory')
        self.fs.set_current_directory('mydirectory')
        self.fs.makedirs('a_dir')
        self.assertNotExist(os.path.sep + 'a_dir')
        self.assertExist('a_dir')
        self.assertExist(os.path.sep + os.path.join('mydirectory', 'a_dir'))

    def test_that_creating_directory_with_absolute_path_is_independent_from_current_directory(self):
        self.fs.makedirs('mydirectory')
        self.fs.set_current_directory('mydirectory')
        self.fs.makedirs(os.path.sep + 'a_dir')
        self.assertExist(os.path.sep + 'a_dir')
        self.assertNotExist('a_dir')
        self.assertExist(os.path.sep + 'a_dir')

    def test_that_nonexistent_directory_cannot_be_removed(self):
        self.assertRaises(FileNotFoundError, self.fs.remove_directory, 'nonexistent')

    def test_that_empty_directory_can_be_removed(self):
        self.fs.makedirs('a_dir')
        self.fs.remove_directory('a_dir')
        self.assertNotExist('a_dir')

    def test_removing_directory_is_affected_by_current_directory(self):
        self.fs.makedirs(os.path.join('a_dir', 'b_dir'))
        self.fs.set_current_directory('a_dir')
        self.assertRaises(FileNotFoundError, self.fs.remove_directory, 'a_dir')
        self.fs.remove_directory('b_dir')
        self.assertNotExist(os.path.sep + os.path.join('a_dir', 'b_dir'))
        self.assertExist(os.path.sep + 'a_dir')
        self.fs.remove_directory(os.path.sep + 'a_dir')
        self.assertNotExist(os.path.sep + 'a_dir')

    def test_non_empty_directory_cannot_be_removed(self):
        self.fs.makedirs(os.path.join('a_dir', 'b_dir'))
        self.assertRaises(OSError, self.fs.remove_directory, 'a_dir')


class TestFilesystemsRWMethods(FileSystemTest):

    def test_that_a_file_can_be_written_and_its_content_can_be_read(self):
        self.fs.write('apple', 'some\ntext')
        self.assertExist('apple')
        self.assertEqual('some\ntext', self.fs.read('apple'))

    def test_that_a_file_in_subdirectory_can_be_written(self):
        self.fs.makedirs('a_dir')
        self.fs.write(os.path.join('a_dir', 'a_file'), 'something')
        self.assertEqual('something', self.fs.read(os.path.join('a_dir', 'a_file')))

    def test_that_reading_nonexistent_file_triggers_not_found_error(self):
        self.assertRaises(FileNotFoundError, self.fs.read, 'nonexistent')

    def test_that_nonexistent_parent_directory_triggers_not_found_error(self):
        self.assertRaises(FileNotFoundError, self.fs.write, os.path.join('nonexistent', 'a_file'), 'anything')
        self.assertRaises(FileNotFoundError, self.fs.read, os.path.join('nonexistent', 'a_file'))

    def test_that_read_and_write_are_affected_by_current_directory(self):
        self.fs.makedirs('a_dir')
        self.fs.set_current_directory('a_dir')
        self.fs.write(os.path.sep + 'a_file', 'hello')
        self.fs.write('b_file', 'world')
        self.assertEqual('hello', self.fs.read(os.path.join('..', 'a_file')))
        self.assertEqual('world', self.fs.read('b_file'))
        self.assertEqual('world', self.fs.read(os.path.sep.join(['', 'a_dir', 'b_file'])))
