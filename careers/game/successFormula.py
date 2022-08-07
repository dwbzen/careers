'''
Created on Aug 5, 2022

@author: don_bacon
'''

class SuccessFormula(object):
    '''
    Encapsulates a player's success formula for a given game.
    '''

    def __init__(self, stars=0, hearts=0, cash=0):
        '''
        Constructor
        '''
        self._fame = stars
        self._happiness = hearts
        self._cash = cash
        
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
        return f'money: ${self._cash},000  fame: {self._fame}  happiness: {self._happiness}'

    def total_points(self):
        return self.cash() + self.fame() + self.happiness()
    
    