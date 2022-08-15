'''
Created on Aug 12, 2022

@author: don_bacon
'''
import random
from game.successFormula import SuccessFormula

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
    
    @staticmethod
    def roll(number_of_dice):
        return random.choices(population=[1,2,3,4,5,6],k=number_of_dice)
        