'''
Created on Jun 4, 2023

@author: don_bacon

'''
from game.careersGame import CareersGame
from game.gameState import GameState
from game.gameUtils import GameUtils
from game.plugins import Plugin
from typing import Dict
import random

class Careers_All_Strategy(Plugin):
    """Implements a basic strategy for a computer player.
        Randomly choose what to do this turn:
            roll, 
            use experience, 
            use opportunity - if entrance criteria met
        Also bump (if any players are 'bumpable'), and retire if possible to do so

        If the player's cash is <=0, issue a "bankrupt"
    """    
    
    def __init__(self, thegame:CareersGame):
        super().__init__(thegame.edition_name)
        self._careersGame = thegame
        self._game_state = self._careersGame.game_state
        seconds = GameUtils.time_since()
        random.seed(seconds)
        
    @property
    def careers_game(self) ->CareersGame:
        return self._careersGame
        
    def run(self, player_number:int) ->Dict:
        """Implement the plugin interface for this class
        """
        result = {}
        if player_number >=0:
            cmds = self._get_turn_commands(player_number)
            result = {"player_number":player_number, "commands":cmds }
            
        return result
    
    def test(self)->str:
        return "Careers_All_Strategy"
    
    def _get_turn_commands(self, player_number:int) ->Dict:
        """Returns a List of commands for a player's turn.
            Commands delimited by semi-colon, for example: "roll;next"
            The last command is always "next" to advance to the next player.
        """
        commands = ["roll"]   # TODO - pick opportunity, experience, or roll
        player = self._game_state.players[player_number]
        if player.cash <= 0:
            commands.append(";bankrupt")
        else:
            #
            # can I bump anyone? If so pick a bumpable player at random
            #
            if len(player.can_bump) > 0:
                num = random.randint(0, len(player.can_bump)-1)
                commands.append(f";bump {player.can_bump[num]}")
                
        commands.append(";next")

if __name__ == '__main__':
    pass

