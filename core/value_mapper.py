"""
.. module:: emotional_mapper
   :synopsis: Emotional Mapper Module

.. moduleauthor:: Adnan AL RIFAI <adnan.alrifai@qemotion.com>
"""
from typing import TypeVar
from typing import Union
from collections import defaultdict

# Create a type
redis_type = TypeVar("RedisConnector")
string_match_type = TypeVar("StringMatch")
fuzzy_match_type = TypeVar("FuzzyMatch")

class ValueMapper:
    """
    Class the map words to emotions
    """
    def __init__(
            self, redis_obj: redis_type,
            string_match: string_match_type,
            fuzzy_match: fuzzy_match_type):
        """
        connect to Redis cluster (constructor) and fill the String
        Matching object with patterns

        :param redis_obj: connection to a redis db containing patterns 
        :type redis_ob: redis_type
        :param string_match: pattern match object
        :type string_match: string_match_type
        :param fuzzy_match: fuzzy match object
        :type fuzzy_match: fuzzy_match_type
        :return:
        :rtype:
        """
        self.redis = redis_obj
        self.sm = string_match
        # Call all keys in the dictionary Redis
        patterns = redis_obj.get_keys()
        # fill the string match obj
        self.sm.add(patterns)
        # fill the Fuzzy Set by simple patterns only
        self.fm = fuzzy_match
        self.fm.add(
            [x for x in patterns if len(x.strip().split(' ')) <= 1]) 
        

    def get_keys(self, keys: Union[str, list]):
        """
        set dictionary in the Redis cache

        :param keys: Keys to lookup for in the cache
        :type keys: Union[str, list]
        :return: map key-values
        :rtype: dict
        """
        pass

    def set_keys(self, dictionary: dict):
        """
        set dictionary in the Redis cache

        :param dictionary: values to set in the Redis cache
        :type dictionary: dict
        :return:
        :rtype:
        """
        pass

    def map(self, string: str) -> dict:
        """
        Return emotional words with teir corresponding values

        :param string: verbatim
        :type string: str
        :return: emotional values and their positions in the string
        :rtype: dict
        """
        # setting results
        results = {}
        # match patterns in the verbatim
        found_patterns = self.sm.match(string)
        # found patterns (words)
        keys = list(found_patterns.keys())
        # replace unfound simple patterns
        unfound_keys = self.fm.replace_unfound(
            string = string, found_patterns = keys, min_len = 4)
        unfound_values = defaultdict(list)
        for key, value in unfound_keys.items():
            unfound_values[value].append(key)
        # Get emotions
        emotional_values = self.redis.get_values(
            keys + list(unfound_keys.values()))
        # Replaced words emotions
        emotional_values_replaced = emotional_values[len(keys):]
        emotional_values_correct = emotional_values[:len(keys)]
        # Add replaced field
        # TODO: Refact, when the name is a list, replaced multiple
        # time, optimize it
        emotional_replaced_new = []
        for value in emotional_values_replaced:
            if isinstance(unfound_values[value['name']], list):
                for element in unfound_values[value['name']]:
                    value['replaced_by']=value['name']
                    value['positions'] = self.sm.find(
                        value['name'], string)
                    value['name'] = element
                    emotional_replaced_new.append(value)
            else:
               value['replaced_by']=value['name']
               value['positions'] = self.sm.find(value['name'], string)
               value['name'] = unfound_values[value['name']]
               emotional_replaced_new.append(value) 
        # add positions to emotional_values correct ones
        for pattern in emotional_values_correct:
            pattern["positions"] = found_patterns[
                pattern["name"].strip()]
        # Return results
        all_emotional_values = (
            emotional_values_correct + emotional_replaced_new)
        # return [{'name': x['name']} for x inq
        return  {x['name']: x  for x in all_emotional_values}
            
            
    
            



if __name__ == '__main__':
    host = ('dictionary-cache.eba-a46hhtky.'
            'eu-west-3.elasticbeanstalk.com')
    r = RedisConnector(host=host, port=6379, db=0)
    sm = StringMatch()
    fm = FuzzyMatch()
    em = EmotionalMapper(r, sm, fm)
