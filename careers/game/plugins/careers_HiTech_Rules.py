'''
Created on May 23, 2023

@author: don_bacon
'''
from game.plugins.plugin import Plugin
from game.careersGame import CareersGame
from typing import Dict

class Careers_HiTech_Rules(Plugin):
    '''
    Implement mandatory rules for the Hi-Tech edition
    '''

    def __init__(self, thegame:CareersGame):
        '''
        Constructor
        '''
        super().__init__(thegame.edition_name)
        self._careersGame = thegame
        self._game_state = self._careersGame.game_state

    def run(self, player_number:int) ->Dict:
        """Implement the plugin interface for this class
        """
        result = {}
        return result
    