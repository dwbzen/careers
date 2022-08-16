'''
Created on Aug 5, 2022

@author: don_bacon
'''

from game.careersObject import CareersObject

class SuccessFormula(CareersObject):
    '''
    Encapsulates a player's success formula for a given game.
    '''

    def __init__(self, stars=0, hearts=0, cash=0):
        """Initialize the success formula with the number of stars (Fame), hearts (Happiness) and cash (money in 1000s) specified.
            Computes game_total_points as the sum.
        
        """
        self._fame = stars
        self._happiness = hearts
        self._cash = cash
        self._game_total_points = stars + hearts + cash
        
    @property
    def fame(self):
        return self._fame
    @property
    def happiness(self):
        return self._happiness
    @property
    def cash(self):
        return self._cash
    @fame.setter
    def fame(self, value):
        self._fame = value
    @happiness.setter
    def hapiness(self, value):
        self._hapiness = value
    @cash.setter
    def cash(self, value):
        self._cash = value
    
    def __str__(self):
        return f'money: ${self.cash},000  fame: {self.fame}  happiness: {self.happiness}'
    
    def __repr__(self):
        """Returns the JSON serialization of SuccessFormula.
        
        """
        return "{" + f' "money": {self.cash}, "fame": {self.fame}, "happiness": {self.happiness}' + "}"

    def to_JSON(self):
        """Overrides base class method.
        
        """
        return self.__repr__()
    
    @property
    def total_points(self):
        return self._game_total_points
    
    