"""
.. module:: redis_connector
   :synopsis: Redis Connector Module

.. moduleauthor:: Adnan AL RIFAI <adnan.alrifai@qemotion.com>
"""
import json
from typing import Union

import redis

from core.connector import Connector

class RedisConnector(Connector):
    """
    Class to handle connection to a Redis server
    """
    def __init__(self, host: str, port: int, db: Union[str,int]):
        """
        connect to Redis cluster (constructor)

        :param host: host URL
        :type host: str
        :param port: port number
        :type port: int
        :param db: db name
        :type db: Union[str, int]
        :return:
        :rtype:
        """
        self.conn = redis.Redis(host = host, port = port, db = db)

    def get_values(self, keys: Union[str, list]):
        """
        set dictionary in the Redis cache

        :param keys: Keys to lookup for in the cache
        :type keys: Union[str, list]
        :return: map key-values
        :rtype: dict
        """
        # if it is one key
        if isinstance(keys, str):
            return json.loads(self.conn.get(keys))
        # if it is multiple key
        elif isinstance(keys, list):
            return [json.loads(x) for x in
                    self.conn.mget(keys) if x]

    def set_values(self, dictionary: dict):
        """
        set dictionary in the Redis cache

        :param dictionary: values to set in the Redis cache
        :type dictionary: dict
        :return:
        :rtype:
        """
        # Accept only Python dict
        if isinstance(dictionary, dict):
            # Transform values of dictionary into string (JSON)
            dictionary = {x: json.dumps(y) for
                          x, y in dictionary.items()}
            try:
                self.conn.mset(dictionary)
            except:
                print("Error")
                print(dictionary)
        else:
            raise TypeError(
                "Invalid argument type: " + str(type(dictionary)))

    def get_keys(self):
        """
        get all keys in the Redis cache database

        :return: all keys
        :rtype: list
        """
        # transform bytes to str
        return [bytes_.decode("utf-8")  for bytes_ in self.conn.keys()]
            



if __name__ == '__main__':
    host = ('dictionary-cache.eba-a46hhtky.'
            'eu-west-3.elasticbeanstalk.com')
    r = RedisConnector(host=host, port=6379, db=0)
    # r.get_keys(" test ")
    # from connectors.core.redis_connector import RedisConnector
    r = RedisConnector(host='localhost', port=6379, db=0)
    r.set_values(
        {"koss estina3e":["la niyeke", "wel da3ara"],
         "kesss":["bez"]}
    )
    r.get_values(["koss estina3e", "kesss"])
