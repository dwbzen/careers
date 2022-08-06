'''
Created on Aug 5, 2022

@author: don_bacon
'''
from .successFormula import SuccessFormula

class Player(object):
    
    def __init__(self, name="Player", salary=2000, cash=2000):
        self._player_name = name
        self._salary = salary
        self._cash = cash
        self.success_formula = SuccessFormula()     # default values
        
    @property
    def player_name(self):
        """Get the player's name."""
        return self._player_name
    
    @player_name.setter
    def player_name(self, value):
        self._player_name = value

    