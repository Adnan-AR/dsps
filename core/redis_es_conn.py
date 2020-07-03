"""
.. module:: redis_es_conn
   :synopsis: Redis Elasticsearch Connector Module

.. moduleauthor:: Adnan AL RIFAI <adnan.alrifai@qemotion.com>
"""
from typing import Union
import re

from elasticsearch import Elasticsearch

from core.connector import Connector
from core.redis_connector import RedisConnector

class RedisEsConnector(Connector):
    """
    Class to handle connection and data transfer between Redis and
    Elasticsearch
    """
    def __init__(
            self, host_es: str, host_redis:str, port_redis: int,
            db_redis: Union[str, int, list]):
        """
        Class constructor
         
        :param host_es: Elasticsearch host URL
        :type host_es: str
        :param host_redis: Redis host URL
        :type host_redis: str
        :param port_redis: Redis port number
        :type port_redis: int
        :param db_redis: Redis db name(s)
        :type db_redis: Union[str, int, list]
        :return:
        :rtype:

        .. note::
            In our application, we create a seperarte db in Redis for
            each document type in Elasticsearch index.

        """
        # Connect to Elasticsearch
        self.es = Elasticsearch(
            hosts=host_es, use_ssl=True, verify_certs=False,
            timeout = 100)
        # Connect to Redis
        if isinstance(db_redis, list):
            self.redis = {db: RedisConnector(
                host=host_redis, port=port_redis, db=db) for
                          db in db_redis}
        else:
            self.redis = {db_redis: RedisConnector(
                host=host_redis, port=port_redis, db=db_redis)}


    def cache_index(self, es_index: str, db_redis: Union[str, int]):
        """
        Reload index data from Elasticsearch to Redis and perform
        some transformation on data
        
        :param es_index: Elasticsearch index name
        :type es_index: str
        :param db_redis: Redis db name
        :type db_redis: Union[str, int]
        :return:
        :rtype:

        .. warnings::
            In our application, we create a seperarte db in Redis for
            each document type in Elasticsearch index.

        """
        # Check if type_ exist as Redis DB (cf. note in documentation)
        
        # Query to retrieve index from Elasticsearch
        es_query = {'match_all': {}}
        # Retrieve data
        scrolls = self.es.search(
            size = 10000, body = {'query': es_query},
            index = es_index, scroll = '1m')
        # scroll over data
        while scrolls['hits']['hits']:
            print("here")
            scroll_id = scrolls['_scroll_id']
            chunk = self.es.scroll(scroll_id=scroll_id, scroll='15m')
            data = {x['_source']['name']: x['_source'] for x
                    in chunk['hits']['hits']}
            # Load data into cache
            self.redis[db_redis].set_values(data)


if __name__ == '__main__':
    conn = RedisEsConnector(
        "https://localhost:9200/", "localhost", 6379, 0)
    conn.cache_index('words')
    
        
        

    
