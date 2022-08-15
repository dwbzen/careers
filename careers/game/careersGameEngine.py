'''
Created on Aug 14, 2022

@author: don_bacon
'''

from careers.game import CareersGame
from game.successFormula import SuccessFormula
from game.player import  Player

class CareersGameEngine(object):
    """CareersGameEngine executes the action(s) associated with each player's turn.
    
    """

    def __init__(self, careersGame:CareersGame):
        '''
        Constructor
        '''
        self._careersGame = careersGame
        self._game_state = self._careersGame.game_state
        

