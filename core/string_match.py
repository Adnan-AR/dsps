"""
.. module:: string_match
   :synopsis: String Matching Module

.. moduleauthor:: Adnan AL RIFAI <adnan.alrifai@qemotion.com>
"""
from glob import glob

from typing import Union
from collections import defaultdict

class StringMatch:
    """
    Class to find `Needles` in a `Haystack`
    """
    def __init__(self):
        """
        Start a String Matching object with an empty patterns set

        :param:
        :type:
        :return:
        :rtype:
        """
        # store patterns in a Set
        self.patterns = set()

    def add(self, patterns: Union[list, str]):
        """
        add a list of patterns or a pattern to the object

        :param patterns: patterns to add to the set
        :type patterns: Union[list, str]
        :return:
        :rtype:
        """
        # If patterns are in a list
        if isinstance(patterns, list) :
            self.patterns = self.patterns.union(set(patterns))
        # if patterns is a string
        elif isinstance(patterns, str) :
            self.patterns.add(patterns)
        # Else raise an error
        else:
            raise TypeError(
                "Invalid argument type: " + str(type(patterns)))


    def remove(self, patterns: Union[list, str]):
        """
        remove a list of patterns or a pattern from the object

        :param patterns: patterns to remove from the set
        :type patterns: Union[list, str]
        :return:
        :rtype:
         """
        # If patterns are in a list
        if isinstance(patterns, list) :
            self.patterns = self.patterns.difference(set(patterns))
        # if patterns is a string
        elif isinstance(patterns, str) :
            self.patterns = self.patterns.difference(set([patterns]))
        # Else raise an error
        else:
            raise TypeError(
                "Invalid argument type: " + str(type(patterns)))

    def match(self, string: str) -> dict:
        """
        match patterns in a string

        :param string: target string
        :type string: str
        :return: positions of matched patterns in the target string
        :rtype: dict
        """
        # length
        length = len(string)
        # func to get all possible substring =< max_pattern_length
        def tokenize(s: str, length: int, max_pattern_length: int):
            dict_ = defaultdict(list)
            for l in range(1, max_pattern_length+1):
                for i in range(length-l+1): dict_[s[i:i+l]].append(i)
            return dict_
        
        def tokenize_1(s: str, length: int, max_pattern_length: int):
            max_l = max_pattern_length
            min_l = 1
            dict_ = defaultdict(list)
            [dict_[i].append(i) for i in range(min_l, max_l + 1)
                 for subl in map(''.join, zip(*[s[i:] for i in range(i)]))]
            return dict_
        
        def tokenize_2(s: str, length: int, max_pattern_length: int):
            maxl = max_pattern_length
            minl = 1
            dict_ = defaultdict(list)
            [dict_[i].append(s[i:i+j]) for i in range(length-minl)
                 for j in range(minl,maxl+1)]
            return dict_
        
        # tokenize the string
        tok =  tokenize(
            s = string, length = length, max_pattern_length=122)
        # Intersection of tokens with patterns
        matches = self.patterns.intersection(tok)
        # return dictionary of results {pattern:offset}
        return {patt: tok[patt] for patt in matches}

    def find(self, sub: str, string: str):
        """
        find all indexes of a substring in a string

        :param sub: substring to find
        :type sub: str
        :param string: target string
        :type string: str
        :return: positions of the substring in the target string
        :rtype: list
        """

        def tokenize(s: str, length: int, range_: int):
            dict_ = defaultdict(list)
            for i in range(length-range_+1):
                dict_[s[i:i+range_]].append(i)
            return dict_

        tok = tokenize(string, length = len(string), range_ = len(sub))
        return tok[sub]
    
