import unittest
import datetime


from test.core.dummy_words import dummy_words
from test.core.dummy_words import dummy_words_expected 
from core.data_transformer import DataTransformer

class TestDataTransformer(unittest.TestCase):
    """
    basic String Match tests
    """    
    def test_1_transform_date(self):
        print("Test 1: `Transform_date` Transform a string date"
              " to datetime object")
        """
        Transform strign date to datetime object
        """
        # Init transformer
        dt = DataTransformer()
        # dummy data
        dummy_data = "2000-09-12T19:59:56.564Z"
        # expected results
        expected_results = datetime.datetime.strptime(
            dummy_data, '%Y-%m-%dT%H:%M:%S.%fZ')
        # Assert
        self.assertEqual(
            dt.transform_date(dummy_data), expected_results)


    def test_2_transform_emotional_dict(self):
        print("Test 2: `transform_emotional_dict` Apply" 
              " transformation on emojis, simple word and"
              " compound word")
        """
        Transform strign date to datetime object
        """
        # Init transformer
        dt = DataTransformer()
        # transform data
        transformed_data = dt.transform_emotional_dict(dummy_words)
        print(transformed_data)
        # Expected results
        # Assert
        self.assertEqual(transformed_data, dummy_words_expected)
