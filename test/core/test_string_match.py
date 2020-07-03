import unittest

from core.string_match import StringMatch

class TestStringMatch(unittest.TestCase):
    """
    basic String Match tests
    """    
    def test_1_add(self):
        print("Test 1: `add` on an empty String Match Object")
        """
        add to an empty String Match object (single pattern)
        """
        # Init empty String Match object
        sm = StringMatch()
        # Add string patterns
        sm.add("test 0")
        sm.add("test 1")
        # Assert
        self.assertEqual(
            set(["test 0","test 1"]), sm.patterns)

    def test_2_add(self):
        print("Test 2: `add` on a non-empty String Match Object")
        """
        add to a non-empty String Match object (list of patterns)
        """
        # init pattern
        first_pattern = "test 0"
        # patterns list
        list_to_add = ["test 0", "test 1", "test 2"]
        # Init empty String Match object
        sm = StringMatch()
        # Add string patterns
        sm.add(first_pattern)
        sm.add(list_to_add)
        # Assert
        self.assertEqual(
            set(list_to_add+[first_pattern]), sm.patterns)

    def test_3_remove(self):
        print("Test 3: `remove` pattern from "
              "non-empty String Match object")
        """
        remove a single pattern from non-empty String Match object
        """
        # init pattern
        pattern_to_remove = "test 0"
        # patterns list
        list_ = ["test 0", "test 1", "test 2"]
        # expected results
        list_expected = ["test 1", "test 2"]
        # Init empty String Match object
        sm = StringMatch()
        # Add string patterns
        sm.add(list_)
        # remove
        sm.remove(pattern_to_remove)
        # Assert
        self.assertEqual(set(list_expected), sm.patterns)

    def test_4_remove(self):
        print("Test 4: `remove` patterns (list) from "
              "non-empty String Match object")
        """
        remove patterns from non-empty String Match object
        """
        # init pattern
        pattern_to_remove = ["test 0", "test 1"]
        # patterns list
        list_ = ["test 0", "test 1", "test 2"]
        # expected results
        list_expected = ["test 2"]
        # Init empty String Match object
        sm = StringMatch()
        # Add string patterns
        sm.add(list_)
        # remove
        sm.remove(pattern_to_remove)
        # Assert
        self.assertEqual(set(list_expected), sm.patterns)

    def test_5_remove(self):
        print("Test 5: `remove` patterns (list) from "
              "empty String Match object")
        """
        remove patterns from empty String Match object
        """
        # init pattern
        pattern_to_remove = ["test 0", "test 1"]
        # expected results
        list_expected = []
        # Init empty String Match object
        sm = StringMatch()
        # remove
        sm.remove(pattern_to_remove)
        # Assert
        self.assertEqual(set(list_expected), sm.patterns)

    def test_6_remove(self):
        print("Test 6: `remove` pattern (string) from "
              "a non-empty String Match object")
        """
        remove pattern (single pattern) from empty String Match object
        """
        # init pattern
        pattern_to_remove = "test 0"
        # expected results
        list_expected = []
        # Init empty String Match object
        sm = StringMatch()
        # remove
        sm.remove(pattern_to_remove)
        # Assert
        self.assertEqual(set(list_expected), sm.patterns)

    def test_7_match(self):
        print("Test 7: `match` patterns from in a string")
        """
        match patterns in a string
        """
        # init pattern
        patterns = ["test 0", "test 1", "test 2"]
        # target string
        string = ("je test 0 puis je test 3 mais j'ai "
                  "loupé test 2 et encore une fois, test 2")
        # expected results
        expected = {"test 0": [3] , "test 2": [41, 68]}
        # Init empty String Match object
        sm = StringMatch()
        # add
        sm.add(patterns)
        # Assert
        self.assertEqual(expected, sm.match(string))

