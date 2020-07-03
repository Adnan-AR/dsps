"""
.. module:: fuzzy_match
   :synopsis: Fuzzy Matching Module

.. moduleauthor:: Adnan AL RIFAI <adnan.alrifai@qemotion.com>
"""
from typing import Union
from collections import defaultdict

from cfuzzyset import cFuzzySet as FuzzySet


class FuzzyMatch:
    """
    class to replace string from a set of words using Fuzzy search
    approach
    """
    def __init__(self):
        """
        start a Fuzzy Match object with an empty set

        :param:
        :type:
        :return:
        :rtype:
        """
        self.fuzzy_set = FuzzySet()

    def add(self, words: Union[list, str]):
        """
        add a list of string or a string to the object

        :param patterns: strings to add to the set
        :type patterns: Union[list, str]
        :return:
        :rtype:
        """
        # If patterns are in a list
        if isinstance(words, list) :
            for word in words:
                self.fuzzy_set.add(word)
        # if patterns is a string
        elif isinstance(words, str) :
            self.fuzzy_set.add(words)
        # Else raise an error
        else:
            raise TypeError(
                "Invalid argument type: " + str(type(words)))

    def most_similar(self, words: list, threshold = 0.75) -> dict:
        """
        replace a list of word to the most similar

        :param words: list of string the unknown words
        :type words: list
        :param threshold: modify if > threshold, default 0.75
        :type threshold: float
        :return: replaced strings
        :rtype: dict
        """
        def replace(word: str, threshold = threshold) -> str:
            """
            Use FuzzySet to modify a list of word to the most similar

            :param word: target string
            :type word: string
            :param threshold: modify if > threshold, default 0.75
            :type threshold: float
            :return: string
            """
            # Get first word (most_similar_word, similarity), if no
            # word is found (None Type), it returns the same word
            try:
                (sim, sim_word), *tail = self.fuzzy_set.get(word)
            except TypeError:
                return word
            # return most similar only if similarity >= threshold
            if sim >= threshold: return sim_word
            else: return word
            
        return {word: replace(word) for word in words}

    def replace_unfound(
            self, string: str, found_patterns: list,
            min_len: int)-> dict:
        """
        replace unfound words in a string by the most similar words

        :param string: target string (no punctuations and lower case)
        :type string: str
        :param found_patterns: found patterns in the target string
        :type found_patterns: list
        :param min_len: minimum length of replaceable strings
        :type min_len: int
        :return: replaced strings
        :rtype: dict
        """
        # reverse sort found_patterns by length of patterns
        found_patterns.sort(key=len, reverse=True)
        # Replace found patterns by white space
        for substring in found_patterns:
            string = string.replace(substring, " ")
        # return unfound words list
        unfound_words = [x for x in string.split() if len(x) >= min_len]
        # Replace them by the most similar
        return self.most_similar(words = unfound_words)

    def commute_values(
            self, string: str, fuzzy_results: dict,
            emotional_values: list) -> list:
        """
        Add the true found patterns and replaced_by field to the
        emotional values

        :param string: target string (no punctuations and lower case)
        :type string: str
        :param fuzzy_results: replacement of unfound words results
        :type fuzzy_results: dict
        :param emotional_values: emotional map values
        :type emotional_values: list
        :return: emotional map values with replaced_by 
            field and positions
        :rtype: list
        """
        # reversed fuzzy_results dict (key: value -> value: [keys])
        unfound_values = defaultdict(list)
        for key, value in fuzzy_results:
            unfound_values[value].append(key) 
        
