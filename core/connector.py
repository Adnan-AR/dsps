"""
.. module:: connector
   :synopsis: Abstract Connector Module

.. moduleauthor:: Adnan AL RIFAI <adnan.alrifai@qemotion.com>
"""

from abc import ABCMeta, abstractmethod

class Connector(object, metaclass=ABCMeta):

    @abstractmethod
    def __init__(self, host):
        self.conn = host
