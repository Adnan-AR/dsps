from time import time

import pandas as pd

from core.redis_connector import RedisConnector
from core.value_mapper import ValueMapper
from core.string_match import StringMatch
from core.fuzzy_match import FuzzyMatch
from core.analyzer import Analyzer

host = ('dictionary-cache.eba-a46hhtky.'
        'eu-west-3.elasticbeanstalk.com')
host='localhost'
r = RedisConnector(host=host, port=6379, db=0)
sm = StringMatch()
fm = FuzzyMatch()
# r.get_keys(" test ")
# from connectors.core.redis_connector import RedisConnector
em = ValueMapper(r, sm, fm)
res_emo = em.map("je très fier")
a = Analyzer(em, None)
print(a.analyse("je très fier et figér "))
string = ("je très fier et figér je très fier et figér  "
         "je très fier et figér je très fier et figér  "
         " Super nice verbatim b ayre khara kleb b ayre"
         " Zob hmar shu hal 2youra heyde b ayre je déteste votre "  
         " application b ayre shu hal eyr heyda b ayre ")
start = time(); b = a.analyse(string); print("time elapsed: ", time()-start)

def func(s, min_l, max_l):
    return [subl for i in range(min_l, max_l + 1)
                 for subl in map(''.join, zip(*[s[i:] for i in range(i)]))]
# the best
def doit(t,minl,maxl):
    parts = [(t[i:i+j],i) for i in range(len(t)-minl) for j in range(minl,maxl+1)]
    return parts

def tokenize(s: str, length: int, max_pattern_length: int):
            dict_ = defaultdict(list)
            for l in range(1, max_pattern_length+1):
                for i in range(length-l+1): dict_[s[i:i+l]].append(i)
            return dict_

# test: for i in range(1,20): start=time(); t=tokenize(string, len(string), 120);print(time()-start)


data = pd.DataFrame([string]*100)
start = time(); data[0].apply(a.analyse); print("time elapsed: ", time()-start)
"""
from core.redis_es_conn import RedisEsConnector

conn = RedisEsConnector(
        "https://localhost:9200/", "localhost", 6379, 0)
conn.cache_index('words')
"""
