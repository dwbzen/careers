'''
Created on Jun 4, 2023

@author: don_bacon

'''
from game.careersGame import CareersGame
from game.gameState import GameState
from game.gameUtils import GameUtils
from game.plugins import Plugin
from game.gameConstants import StrategyLevel, BorderSquareType
from game.gameEngineCommands import GameEngineCommands
from typing import Dict, List
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
    
    def __init__(self, thegame:CareersGame, level:str="dumb"):
        super().__init__(thegame.edition_name)
        self._careersGame:CareersGame = thegame
        self._game_state:GameState = self._careersGame.game_state
        seconds = GameUtils.time_since()
        random.seed(seconds)
        self._strategy_level:StrategyLevel = StrategyLevel[level.upper()]
        self._gameEngineCommands = None
        
    @property
    def careers_game(self) ->CareersGame:
        return self._careersGame
    
    @property
    def strategy_level(self):
        return self._strategy_level
    
    @strategy_level.setter
    def strategy_level(self, value):
        self._strategy_level = value
        
    @property
    def gameEngineCommands(self):
        return self._gameEngineCommands
    
    @gameEngineCommands.setter
    def gameEngineCommands(self, value):
        self._gameEngineCommands = value
        
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
    
    def _get_turn_commands(self, player_number:int) ->str:
        """Returns a List of commands for a player's turn.
            Commands delimited by semi-colon, for example: "roll;next"
            The last command is always "next" to advance to the next player.
        """
        commands = []
        player = self._game_state.players[player_number]
        if player.cash <= 0:
            commands.append("bankrupt")
        else:
            #
            # can I bump anyone? If so pick a bumpable player at random
            #
            if len(player.can_bump) > 0:
                num = random.randint(0, len(player.can_bump)-1)
                commands.append(f";bump {player.can_bump[num]}")

        advance_cmds = self._pick_advance_command(player)
        commands.append(advance_cmds)    # pick opportunity, experience, or roll
                
        commands.append("next")
        return ";".join(commands)
        
    def _pick_advance_command(self, player) ->str:
        """Pick an advancement command based the StrategyLevel.
            DUMB - If occupying an occupation entrance square, and can afford it (or has been there before or has a degree)
                   then enter and roll, otherwise returns only "roll"
                   Also resolve pending actions: "select_degree", "buy_insurance" 
            BASIC - randomly pick roll, use experience, use opportunity
                    Player must be able to afford the opportunity cost, for example
                    when entering an occupation or buying insurance, hearts, or stars
            SMART - BASIC + consider what helps fulfill the success formula
            GENIUS - use trained neural network model
            
            Note - only DUMB strategy is currently implemented.
            The strategy level is set from the plugins section of editions.json
            
        """
        commands = []
        my_location = player.board_location
        border_square = self.careers_game.game_board.get_square(my_location.border_square_number)    # BorderSquare
        if border_square.square_type is BorderSquareType.OCCUPATION_ENTRANCE_SQUARE and my_location.occupation_name is None:
            #
            # okay to enter the Occupation if the player can afford it, has the right degree, or has been there before
            #
            occupation_name = border_square.name
            commands.append(f"enter {occupation_name}")    # this could ERROR if the player doesn't meet the occupation entrance criteria
    
        match(self.strategy_level):
            case StrategyLevel.DUMB:
                commands.append("roll")
            case _:
                commands.append("roll")
        
        return ";".join(commands)

if __name__ == '__main__':
    print(Careers_All_Strategy.__doc__)

