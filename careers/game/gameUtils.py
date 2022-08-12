'''
Created on Aug 12, 2022

@author: don_bacon
'''
import random

class GameUtils(object):
    """
    General purpose routines.
    """

    def __init__(self, params):
        pass
    
    @staticmethod
    def shuffle(size:int) -> list:
        return random.sample(list(range(0, size)), size)
    