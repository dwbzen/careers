'''
Created on Jun 4, 2023

@author: don_bacon

'''
from game.careersGame import CareersGame
from game.gameState import GameState
from game.gameUtils import GameUtils
from game.plugins import Plugin
from game.opportunityCard import OpportunityCard
from game.experienceCard import ExperienceCard
from game.gameConstants import StrategyLevel, BorderSquareType, PendingActionType
from game.gameEngineCommands import GameEngineCommands
from typing import Dict, List
import random

class Careers_All_Strategy(Plugin):
    """Implements various strategies for a computer player.
        Strategy levels are configured in editions.json under "plugins" as StrategyLevel
        
        Randomly choose what to do this turn:
            roll, 
            use experience, 
            use opportunity - if entrance criteria met
        Also bump (if any players are 'bumpable'), and retire if possible to do so
        If the player's cash is <=0, issue a "bankrupt"
        
        Notes - the GameEngineCommands reference, initially None, is set by
        the CareersGameEngine done() method.
    """    
    
    def __init__(self, thegame:CareersGame, level:str="dumb"):
        super().__init__(thegame.edition_name)
        self._careersGame:CareersGame = thegame
        self._game_state:GameState = self._careersGame.game_state
        seconds = GameUtils.time_since()
        random.seed(seconds)
        self._strategy_level:StrategyLevel = StrategyLevel[level.upper()]
        self._gameEngineCommands = None
        self._possible_actions = ["roll", "use opportunity", "use experience"]
        
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
            The commands set here apply to all strategy levels.
            The following pending_actions are resolved: SELECT_DEGREE, TAKE_SHORTCUT, BUY_INSURANCE
            
        """
        commands = []
        player = self._game_state.players[player_number]
        if player.cash <= 0:
            commands.append("bankrupt")
        elif player.pending_actions.size() > 0:
            #
            # Resolve pending action(s)
            #
            for pending_action in player.pending_actions.pending_actions:
                pending_action_value = pending_action.pending_action_type.value
                if pending_action.pending_action_type is PendingActionType.SELECT_DEGREE:
                    #
                    # pick a degree at random
                    #
                    degree = self._careersGame.pick_degree()
                    commands.append(f"resolve {pending_action_value} {degree}")
                elif pending_action.pending_action_type is PendingActionType.TAKE_SHORTCUT:   # random yes or not
                    selection = random.sample(['yes','no'], 1)[0]
                    commands.append(f"resolve {pending_action_value} {selection}")
                elif pending_action.pending_action_type is PendingActionType.BUY_INSURANCE:   # int dollar amount
                    if player.cash > pending_action.pending_amount:
                        commands.append(f"resolve {pending_action_value} {pending_action.pending_amount}" )
                elif pending_action.pending_action_type is PendingActionType.BUY_HEARTS:
                    pass
        else:
            #
            # can I bump anyone? If so pick a bumpable player at random
            #
            if len(player.can_bump) > 0:
                num = random.randint(0, len(player.can_bump)-1)
                commands.append(f"bump {player.can_bump[num]}")

        advance_cmds = self._pick_advance_commands(player)
        commands.append(advance_cmds)    # pick opportunity, experience, or roll
                
        commands.append("next")
        return ";".join(commands)
        
    def _pick_advance_commands(self, player) ->str:
        """Pick an advancement command based the StrategyLevel.
            DUMB - If occupying an occupation entrance square, and can afford it (or has been there before or has a degree)
                   then enter and roll, otherwise returns only "roll"
                   Also resolve pending actions: "select_degree", "buy_insurance" 
            BASIC - randomly pick roll, use experience, use opportunity
                    Player must be able to afford the opportunity cost, for example
                    when entering an occupation or buying insurance, hearts, or stars
            SMART - BASIC + consider what helps fulfill the success formula
            GENIUS - use trained neural network model
            
            The strategy level is configured in the plugins section of editions.json
            
        """
        commands = []
        my_location = player.board_location
        border_square = self.careers_game.game_board.get_square(my_location.border_square_number)    # BorderSquare
        can_enter = (False, 0, "", "")
        if border_square.square_type is BorderSquareType.OCCUPATION_ENTRANCE_SQUARE and my_location.occupation_name is None:
            #
            # okay to enter the Occupation if the player can afford it, has the right degree, or has been there before
            # the gameEngineCommands can_enter function determines if the player can enter the occupation.
            #
            occupation_name = border_square.name
            occupation = self.careers_game.occupations[occupation_name]
            # can_enter tupple is meets_criteria (bool), entry_fee (int), message (str), occupation.name (str)
            can_enter = self._gameEngineCommands.can_enter(occupation, player)
            
            # commands.append(f"enter {occupation_name}")    # this could ERROR if the player doesn't meet the occupation entrance criteria
    
        match(self.strategy_level):
            case StrategyLevel.DUMB:
                commands.append(self.dumb_strategy(player, can_enter))
            case StrategyLevel.BASIC:
                commands.append(self.basic_strategy(player), can_enter)
            case StrategyLevel.SMART:
                commands.append(self.smart_strategy(player), can_enter)
            case _:
                commands.append("roll")
        
        return ";".join(commands)

    def dumb_strategy(self, player, can_enter) ->str:
        """If you are on an occupation entrance square AND can enter it, then do it, else just roll.
            Arguments:
                player - Player reference
                can_enter - a 4-tupple result from gameEngineCommands.can_enter()
            Returns:
                List[str] of commands
        """
        if can_enter[0]:
            commands = f"enter {can_enter[3]};roll"
        else:
            commands = "roll"
        return commands
    
    def basic_strategy(self, player, can_enter) ->str:
        """Randomly select an action from "roll", "use opportunity", "use experience"
            The player must be able to use the opportunity and meet the entrance criteria if it's an occupation.
            If no opportunities apply, then default to use experience.
            If use experience, select the one at random.
            If no experience cards, default to roll
        """
        #if player.is_sick or player.is_unemployed:

        actions = random.sample(["roll", "use opportunity", "use experience"], 3)    # returns the list in random order
        for action in actions:
            if action.endswith("opportunity"):
                #
                # select an opportunity at random
                #
                for opportunity_card in player.my_opportunity_cards:
                    pass
                
        return "roll"
    
    def smart_strategy(self, player, can_enter) ->str:
        """Applies additional smarts to the basic strategy.
            This will attempt to pick the best Opportunity card
            or Experience card for the player's circumstances -
            including board position, success formula fulfillment.
        """
        return "roll"
    
if __name__ == '__main__':
    print(Careers_All_Strategy.__doc__)

