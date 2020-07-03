"""
.. module:: dictionary_connector
   :synopsis: Dictionary Connector Module

.. moduleauthor:: Adnan AL RIFAI <adnan.alrifai@qemotion.com>
"""
from typing import Union

from core.redis_es_conn import RedisEsConnector

class DictionaryConnector(RedisEsConnector):
    """
    Class that inherit Redis Es Connector and override the private
    __set method, that excute LUA script to check if the key is
    is already there and replace it only on a condition
    """
    def __init__(
            self, host_es: str, host_redis:str, port_redis: int,
            db_redis: Union[str, int]):
        """
        Class constructor
         
        :param host_es: Elasticsearch host URL
        :type host_es: str
        :param host_redis: Redis host URL
        :type host_redis: str
        :param port_redis: Redis port number
        :type port_redis: int
        :param db_redis: Redis db name
        :type db_redis: Union[str, int]
        :return:
        :rtype:
        """
        super().__init__(
            host_es= host_es, host_redis= host_redis,
            port_redis= port_redis, db_redis= db_redis)

    def cache_index(self, es_index):
        """
        Override the parent function to load emotional dictioanry
        and use collapse and sort to avoid duplicate emotional words
        and select the most recet updated one.
        
        :param es_index: Elasticsearch index name
        :type es_index: str
        :return:
        :rtype:
        """ 
        # Query to retrieve emotional words from
        es_query = {
            "query": {"match_all": {}},
            "sort":[{"updated_at":"desc"}],
            "collapse" : {"field" : "name.keyword"}
        }
        es_query_2 = {
            "query": {"match_all": {}}
        }
        es_query_3_1 = {
            "aggs": {
                "maximum_match_counts": {
                    "cardinality": {
                        "field": "name.keyword",
                        "precision_threshold": 100
                    }
                }
            }
        }
        
        # Retrive Cardinality
        card = self.es.search(
            size = 0, body = es_query_3_1, index = es_index)

        es_query_3_2 ={
            "aggs":{
                "duplicateCount": {
                    "terms": {
                        "field": "name.keyword",
    			"size":card['aggregations'][
                            'maximum_match_counts']['value'],
    			"min_doc_count": 2
                    },
                    "aggs": {
                        "duplicateDocuments": {
                            "top_hits": {
    				"_source":["name","updated_at"],
    				"sort": [
                                    {"updated_at":{"order":"desc"}}
                                ],
    				"size": 1
                            }
    			}
    		    }
                }
            }
        }
        
        # Retrieve data
        scrolls = self.es.search(
            size = 10000, body = es_query_3_2,
            index = es_index, scroll = '1m')
        # Print the data here
        #############################################################
        # Retrieve data
        scrolls = self.es.search(
            size = 10000, body = es_query_3_2,
            index = es_index, scroll = '1m')
        # scroll over data
        while scrolls['hits']['hits']:
            print("here")
            scroll_id = scrolls['_scroll_id']
            chunk = self.es.scroll(scroll_id=scroll_id, scroll='15m')
            data = {x['_source']['name']: x['_source'] for x
                    in chunk['hits']['hits']}
            # Load data into cache
            self.redis.set_values(data)
        #############################################################

if __name__ == '__main__':
    conn = DictionaryConnector(
        "https://localhost:9200/", "localhost", 6379, 0)
    conn.cache_index('words')
