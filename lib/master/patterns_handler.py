"""
.. module:: patterns_handler
   :synopsis: Pattern Handler - Distributed String Matching System

.. moduleauthor:: Adnan AL RIFAI <adnan.alrifai@qemotion.com>
"""
from collections import defaultdict

import numpy as np

class PatternsHandler:
    """
    **Elixir Module implemented in Python**
    Patterns processing before feeding the distributed string
    matching system
    """
    def __init__(self):
        """
        Constructor
        :param:
        :type:
        :return:
        :rtype:
        """
        pass

    @staticmethod
    def chunk_patterns_byworkers(patterns, workers):
        """
        Transform a list of patterns to chunks of list classed by
        length of the pattern

        :param patterns: string patterns
        :type patterns: list
        :param workers: worker names
        :type workers: list
        :return: substrings classed by length of string
        :rtype: dictionary

        :Example:
            >>> patterns = ["test1", "test2", "test3", "test4"
            ...             "test12", "test13"]
            >>> PatternsHandler.chunk_patterns_byworkers(patterns, 2)
            {
                5: [["test1","test2"],["test3","test4"]],
                6: [["test12", "test13"]]
            }
        """
        def chunks(list_, n):
            """
            Yield successive n-sized chunks from lst.
            :param list_: patterns
            :type list_: list 
            :param n: size of chunks
            :type n: integer
            :return: list of sublists
            :rtype: list
            """
            for i in range(0, len(list_), n):
                yield list_[i:i + n]

        def chunk_patterns(list_, n):
            """
            Chunk a list by n steps
            :param list_: patterns
            :type list_: list 
            :param n: number of chunks
            :type n: integer
            :return: list of sublists
            :rtype: list
            """
            list_length = len(list_)
            if list_length < n:
                return chunks(list_, n)
            else:
                return chunks(list_, list_length // n)

        def key_min_value(dictionary):
            """
            Get the key of the smallest value in a dictionary
            :param dictionary: target
            :type dictionary: dictionary
            :return: keys of smallest values
            :rtype: list
            """
            min_val = min(dictionary.values())
            return [k for k, v in dictionary.items() if v == min_val]
        
        # Init defaultdict using type list as a default value
        pattern_chunks = defaultdict(list)
        # Numnber of workers (chunks)
        chunks_num = len(workers)
        # feed the defaultdict
        for pattern in patterns:
            pattern_chunks[len(pattern)].append(pattern)
        # Init workers mapping
        workers_mapping = defaultdict(list)
        # distribute words to workers (smallest worker for each length)
        # TODO: optimize O(n^3)
        for k, v in pattern_chunks.items():
            # reset size for each length
            workers_size = {worker: 0 for worker in workers}
            for word in v:
                smallest_worker = key_min_value(workers_size)
                workers_mapping[smallest_worker[0]].append(word)
                workers_size[smallest_worker[0]] += 1    
        #Chunks by length 
        chunks_bylength = {k: list(chunk_patterns(v, chunks_num)) for (k,v)
                in dict(pattern_chunks).items()}
        # Return the map (results)
        return dict(workers_mapping)
                
                    

class Adnan:
    def __init__(self):
        pass
    @staticmethod
    def test():
        path =  ("/Users/adnan/Qemotion/dsps_system/"
                 "tmp_dict/22_char_words.csv")
        with open(path) as f:
            lines = [line.rstrip() for line in f]
        return PatternsHandler.chunk_patterns_byworkers(lines, ["a","v","c"])


if __name__ == "__main__":
    patterns_1 = ["test1", "test2", "test3", "test4", "test12",
                  "test13", "test14", "test15", "test16"]
    patterns_2 = ["test1", "test2", "test3", "test4", "test12",
                  "test13", "test14", "test15", "test16"]
    print(PatternsHandler.chunk_patterns_byworkers(patterns_2, ["a","b"]))
    
