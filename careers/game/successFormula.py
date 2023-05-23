'''
Created on Aug 5, 2022

@author: don_bacon
'''

from game.careersObject import CareersObject
import json

class SuccessFormula(CareersObject):
    '''
    Encapsulates a player's success formula for a given game.
    '''

    def __init__(self, stars=0, hearts=0, money=0):
        """Initialize the success formula with the number of stars (Fame), hearts (Happiness) and money (money points, in 1000s) specified.
            Computes game_total_points as the sum.
        
        """
        self._stars = stars
        self._hearts = hearts
        self._money = money
        self._game_total_points = stars + hearts + money
        
    @property
    def stars(self):
        return self._stars
    @property
    def hearts(self):
        return self._hearts
    @property
    def money(self):
        return self._money
    @stars.setter
    def stars(self, value):
        self._stars = value
    @hearts.setter
    def hapiness(self, value):
        self._hapiness = value
    @money.setter
    def money(self, value):
        self._money = value
    
    def __str__(self):
        return f'cash: ${self.money},000  stars: {self.stars}  hearts: {self.hearts}  points: {self.total_points} '
    
    def to_dict(self):
        return { "cash" : self.money, "stars" : self.stars, "hearts" : self.hearts, "points" : self.total_points}

    def to_JSON(self):
        """Returns the JSON serialization of SuccessFormula.
        """
        return json.dumps(self.to_dict())
    
    @property
    def total_points(self):
        return self._game_total_points
    
    