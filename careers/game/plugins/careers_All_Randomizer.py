'''
Created on May 23, 2023

@author: don_bacon
'''

from game.careersGame import CareersGame
from game.plugins.plugin import Plugin
from game.todoList import TodoList

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
    
    def run(self, noccupations=2, ndegrees=1) ->Dict:
        """TODO: Implement the plugin interface for this class
            Arguments:
                noccupations - number of occupations to add to the todo list, default = 2
                ndegrees - number of degrees to add to the todo list, default = 1
            Returns: players' TodoList as a Dict 
                todo is a Dict with the the keys "degrees" and "occupations"
                degrees is a 1-element list consisting of a degree name
                occupations is a 2-element list of occupation names
            By rule, a player must complete the occupations and degree programs in order to win.
            Example for 2 occupations, 1 degree:
                {
                    "occupations_todo": [ 
                        {"occupation_name": "SapphireRecords", "complete" : 0 },
                        {"occupation_name": "CottonClub", "complete" : 1}
                    ], 
                    "degrees_todo": [
                        {"degree_name" : "Dance"} 
                    ]
                }
        """
        occupation_names = self._careersGame.occupations_dict["occupations"]
        degree_names = self._careersGame.college_degrees["degreePrograms"]
        degrees = random.sample(degree_names, ndegrees)
        occupations = random.sample(occupation_names, noccupations)
        #
        todo_list = TodoList(occupation_names=occupations, degree_names=degrees)
        result =   todo_list.todos 
        for player in self._game_state.players:
            player.my_todos = todo_list

        return result
    