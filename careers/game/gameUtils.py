'''
Created on Aug 12, 2022

@author: don_bacon
'''
import random
from game import SuccessFormula

class GameUtils(object):
    """
    General purpose routines.
    """

    def __init__(self, params):
        pass
    
    @staticmethod
    def shuffle(size:int) -> list:
        return random.sample(list(range(0, size)), size)
    
    
    @staticmethod
    def get_random_formula(total_points) -> SuccessFormula:
        cash = random.randint(1, total_points)
        hearts = random.randint(1, 100-cash)
        stars = random.randint(1,100-(cash+hearts))
        return SuccessFormula(stars, hearts, cash)
        