'''
Created on May 23, 2023

@author: don_bacon
'''

from game.careersGame import CareersGame
from game.plugins.plugin import Plugin

from typing import Dict
import random

class Careers_All_Randomizer(Plugin):
    '''
    Implements the optional Randomizer feature for selecting mandatory occupation(s) and degree(s).
    '''


    def __init__(self, thegame:CareersGame):
        '''
        Constructor
        '''
        super().__init__(thegame.edition_name)
        self._careersGame = thegame
        self._game_state = thegame.game_state
        
    @property
    def careers_game(self) ->CareersGame:
        return self._careersGame
    
    def test(self)->str:
        return "Careers_All_Randomizer"
    
    def run(self, player_number:int=-1) ->Dict:
        """TODO: Implement the plugin interface for this class
            Arguments:
                player_number - not needed for this plugin. Default is -1, the admin player.
            Returns: A Dict with the keys "player_number" and "todo"
                todo is a Dict with the the keys "degrees" and "occupations"
                degrees is a 1-element list consisting of a degree name
                occupations is a 2-element list of occupation names
            By rule, a player must complete the occupations and degree programs in order to win.
        """
        occupation_names = self._careersGame.occupations_dict["occupations"]
        degree_names = self._careersGame.college_degrees["degreePrograms"]
        degree_name = random.sample(degree_names, 1)[0]
        occupations = random.sample(occupation_names, 2)
        #
        todos = {"occupations" : occupations, "degrees" : [degree_name]}
        result = {"player_number":player_number, "todo":todos }
        for player in self._game_state.players:
                player.my_todos = todos
                
        return result
    