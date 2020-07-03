"""
.. module:: analyzer 
   :synopsis: Analyzer Module

.. moduleauthor:: Adnan AL RIFAI <adnan.alrifai@qemotion.com>
"""
from typing import TypeVar
# TODO: Remove
from time import time

import pandas as pd

from core.redis_connector import RedisConnector
from core.value_mapper import ValueMapper
from core.string_match import StringMatch
from core.fuzzy_match import FuzzyMatch
# TODO: TextTransformer will be deprecated, use DataPreprocesser
# instead
from core.data_preprocessor import TextTransformer
# TODO:
from core.emotional_handler import EmotionalHandler

# Create Value Type mapper
value_mapper_type = TypeVar("ValueMapper")
data_preprocessor_type = TypeVar("DataPreprocessor")


class Analyzer:
    """ 
    Central Unit for emotional analysis
    """
    def __init__(
            self, value_mapper: value_mapper_type,
            data_preprocessor: data_preprocessor_type):
        """
        Constructor of emotional analyzer

        :param value_mapper: Module that map emotional values to found
            patterns
        :type value_mapper: value_mapper_type
        :param data_preprocessor: string pre-processor 
        :type data_preprocessor: data_preprocesser_type
        :return:
        :rtype: 
        """
        # Value mapper
        self.vm = value_mapper
        # Init the text transformer
        self.tt = TextTransformer()

    def analyse(self, verbatim: str) -> dict:
        """
        Compute emotional classification of a verbatim
        
        :param verbatim: verbatim composed of mutliple sentences
        :type verbatim: str 
        :return: emotional classification report
        :rtype: dict 
        """
        # Pre-process the verbatim (including splitting)
        # Transform string
        start = time()
        string_transformed = ' ' + self.tt.separate_words(
            self.tt.multireplace(verbatim)) + ' '
        print("Transform string time: ", time()-start)
        # Get emotional words -> dataframe
        start = time()
        emotional_words = self.vm.map(string_transformed)
        print("Emotional mapping: ", time()-start)
        start = time()
        emotional_df = pd.DataFrame.from_dict(
            emotional_words, orient = 'index')
        print("dict -> df: ", time()-start)
        start = time()
        verbatim_info = (
            0, verbatim, emotional_df, 'fr',
            self.tt.process_string(verbatim)['subtexts'])
        print("filling verbatim_info: ", time()-start)
        # Get subtexts as list of tuple [(sentence, id),...]
        sentences = [(subtext['subtext'], subtext['id'])
                     for subtext in verbatim_info[4]]
        
        # Compute emotions classification
        start = time()
        ea = EmotionalHandler(
            verbatim_id = verbatim_info[0], verbatim = verbatim_info[1],
            language = verbatim_info[3], words_as_df = verbatim_info[2],
            sentences = sentences)
        print("compute emotions: ", time()-start)
        # Getting the result
        return ea.results
