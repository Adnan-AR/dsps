"""
.. module:: data_transformer
   :synopsis: Data transformer

.. moduleauthor:: Adnan AL RIFAI <adnan.alrifai@qemotion.com>
"""
from typing import TypeVar
import datetime
import re

# Create a type
date_type = TypeVar("datetime.datetime")

class DataTransformer:
    """
    Class to handle emotional dictionary data transformation
    """
    def __init__(self):
        """
        Class constructor
        """
        pass

    def transform_date(self, date: str) -> date_type:
        """
        Transform string date (i.e Year-Month-Day:Minutes-secondsZ) 
        to datetime object

        :param date: date and time 
        :type date: string
        :return: date and time
        :rtype: datetime object

        .. note::
            To be removed if not used
        """
        try: return datetime.datetime.strptime(
                date, '%Y-%m-%dT%H:%M:%S.%fZ')
        # error: return the current date and time
        except: return datetime.datetime.now()

    def transform_emotional_dict(self, data: dict) -> dict:
        """
        transform loaded data by applying the following:
        1- add white space on both ends of none `Emote` patterns
        2- verify the `is_compound` field
        3- Remove NaN from certain columns

        :param data: emotional dictional word
        :type data: dict
        :return: transformed emotional word
        :rtype: dict
        """
        def side_padder(string: str):
            """
            This function pad space and in all entries in a string. 
            To be applied on all entries in emotional dictionary.

            :param string: string to be padded
            :type string: str
            :return: string with added spaceds from both side
            :rtype: str
            """
            if string.endswith(' '): return ' ' + string
            else: return ' ' + string + ' '
                  
        transformed_data = {}
        # Regex to check if it contains any char except alphanumeric,
        # white space, end of line and dash
        regexp = re.compile(r'[^a-zA-Z0-9À-ÿ \n-]+')
        for key, value in data.items():
            # Check if it is a compound word
            if key.count(' ') >= 1: value["is_compound_word"] = True
            else: value["is_compound_word"] = False
            # add white space to non emojis word on both end
            if value["is_emote"] and bool(regexp.search(key)):
                transformed_data[key] = value
            else:
                transformed_data[side_padder(key)] = value

        # Return transformed data
        return transformed_data
