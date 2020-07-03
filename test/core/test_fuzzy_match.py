import unittest

from core.fuzzy_match import FuzzyMatch

class TestFuzzyMatch(unittest.TestCase):
    """
    basic Fuzzy Match tests
    """
    def test_1_most_similar(self):
        print("Test 1: `most_similar` on an a list of words")
        """
        Return the most similar words
        """
        # Init empty FuzzySet
        fm = FuzzyMatch()
        # Add string patterns to the Fuzzy Set
        fm.add(["apple","orange","wrong_word"])
        # Match a list of wrong words
        results = fm.most_similar(['appl','rong_word'])
        # Check the returned value
        self.assertEqual(
            {'appl':'apple', 'rong_word':'wrong_word'}, results)

    def test_2_replace_unfound(self):
        print("Test 2: `replace_unfound` on an a string")
        """
        Replace unfound words in string with a respect of minimum 
        length
        """
        # Init empty FuzzySet
        fm = FuzzyMatch()
        # Add string patterns to the Fuzzy Set
        fm.add(["apple","orange","wrong_word"])
        # Replace words
        results = fm.replace_unfound(
            string='i ate the appl stock maybe this is the rong_word',
            found_patterns=['stock','this'], min_len=4)
        # Expected results
        expected_res = {
            'appl':'apple', 'rong_word':'wrong_word', 'maybe':'maybe'}
        # Check the returned results
        self.assertEqual(expected_res, results)
