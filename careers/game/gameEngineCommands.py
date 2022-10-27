'''
Created on Sep 11, 2022

@author: don_bacon
'''

from game.careersGame import CareersGame
from game.commandResult import CommandResult
from game.player import Player
from game.gameUtils import GameUtils
from game.opportunityCard import OpportunityCard, OpportunityType
from game.occupation import Occupation
from game.gameConstants import GameConstants

from typing import Tuple, List
import joblib
import random, json

class GameEngineCommands(object):
    """Implementations of CareersGameEngine commands.
    
    """
    
    def __init__(self, thegame:CareersGame, logfile_pointer):
        self._careersGame = thegame
        self._game_state = self._careersGame.game_state
        self.fp = logfile_pointer
        self._trace = True          # traces the action by describing each step and logs to a file
        self.currency_symbol = self._careersGame.game_parameters.get_param("currency_symbol")
    
    @property 
    def careersGame(self) -> CareersGame:
        return self._careersGame
    
    @careersGame.setter
    def careersGame(self, thegame:CareersGame):
        self._careersGame = thegame
        
    @property
    def trace(self):
        return self._trace
    
    @trace.setter
    def trace(self, value):
        self._trace = value
        
    def can_player_move(self, player:Player, dice:List[int]) -> Tuple[bool,CommandResult] :
        """Determine if a Player can move.
            A player cannot move if bankrupt (cash < 0) and can move from the Hospital or Unemployment
            only if the rolled dice meet the requirements for that game square.
            Arguments:
                player - the current Player
                dice - the player's roll as a List[int], for example [6,5] (I rolled an 11!)
            Returns: a 2-element tupple consisting of a boolean (the player can move or not)
            and a CommandResult.
        """
        if player.is_unemployed or player.is_sick:
            bs_name = player.current_border_square_name()
            # bs_number = player.current_border_square_number
            game_square = self.careersGame.find_border_square(bs_name)
            #
            # let the square determine if the player can move or not
            # as that's encoded in the specialProcessing
            #
            result = game_square.execute_special_processing(player, dice)
        elif player.cash < 0:       # Can't move if bankrupt
            result = CommandResult(CommandResult.NEED_PLAYER_CHOICE, f'You are bankrupt: {self.currency_symbol}{player.cash}, and must either borrow/trade for needed funds or declare Bankruptcy', False)
        else:
            result = CommandResult(CommandResult.SUCCESS, f'Player may move {dice} spaces', True)
            
        can_move = result.is_successful()
        return can_move, result

    def can_enter(self, occupation:Occupation, player:Player):
        """Determine if this player can enter the named Occupation
            This checks if the player meets the entry conditions, namely:
                * it's college and they have the tuition amount in cash
                * they've previously completed this occupation and can therefore enter for free
                * or they have a qualifying degree and can therefore enter for free
                * or they have executed an "All expenses paid" Opportunity card
                * or they have sufficient cash to cover the entry fee 
            Arguments:
                occupation - an Occupation instance
                player - a Player instance
            Returns: tupple -
                [0] bool True if can enter, False otherwise
                [2] entry amount owed, if any. Could be 0
        """

        entry_fee = occupation.entryFee
        has_fee = player.cash >= entry_fee
        occupationClass = occupation.occupationClass
        # anyone can go to college if they have the funds
        if occupationClass == 'college':
            if has_fee:
                return (True, entry_fee)    # always pay for college
            else:    # Can't afford College
                return (False, entry_fee)
        
        #
        # check occupation record for prior trips through 
        #
        if occupation.name in player.occupation_record and player.occupation_record[occupation.name] > 0:
            return (True, 0)
        #
        # check degree requirements
        #
        degreeRequirements = occupation.degreeRequirements
        degreeName = degreeRequirements['degreeName']
        numberRequired = degreeRequirements['numberRequired']
        if degreeName in player.my_degrees and player.my_degrees[degreeName] >= numberRequired:
            return (True, 0)        # can enter for free
        #
        # is the player using a  "All expenses paid" Opportunity card ?
        #
        if player.opportunity_card is not None:
            if player.opportunity_card.expenses_paid:
                return (True, 0)
        
        return has_fee, entry_fee

    @staticmethod
    def parse_command_string(txt:str, addl_args=[]) -> CommandResult:
        """Parses a command string into a string that can be evaluated with eval()
            Returns: if return_code == 0, a CommandResult with commandResult.message as the string to eval()
                else if return_code == 1, commandResult.message has the error message
        """
        command_args = txt.split()
            
        command = command_args[0]
        if not command in GameConstants.COMMANDS:
            return CommandResult(CommandResult.ERROR,  f'Invalid command: "{command}"',  False)
        if len(command_args) > 1:
            args = command_args[1:]
            command = command + "("
            for arg in args:
                if arg.isdigit():
                    command = command + arg + ","
                else:
                    command = command + f'"{arg}",'
        
            command = command[:-1]    # remove the trailing comma
        else:
            command = command + "("
            
        if addl_args is not None and len(addl_args) > 0:
            for arg in addl_args:
                command = command + f'"{arg}",'
            command = command[:-1]
        if len(command_args) == 2 and command_args[0].lower().startswith("resolve"):
            # add the choice argument for resolve command as 'none'
            command += f',"none")'
        else:
            command += ")"
        
        return CommandResult(CommandResult.SUCCESS, command, False)
    
    @staticmethod
    def list(player, what) ->CommandResult:
        """List the Experience or Opportunity cards held by the current player
            Arguments: what - 'experience', 'opportunity', or 'all'
            Returns: CommandResult.message is the stringified list of str(card).
                For Opportunity cards this is the text property.
                For Experience cards this is the number of spaces (if type is fixed), otherwise the type.
            
        """
        listall = (what.lower() == 'all')
        list_dict = {}
        if what.lower().startswith('opp') or listall:    # list opportunity cards
            ncards = len(player.my_opportunity_cards)
            list_dict['number_opportunity_cards'] = ncards
            if ncards > 0:
                list_dict['opportunity_cards'] = [cd.to_dict() for cd in player.my_opportunity_cards]
                    
        if what.lower().startswith('exp') or listall:    # list experience cards
            ncards = len(player.my_experience_cards)
            list_dict['number_experience_cards'] = ncards
            if ncards > 0:
                list_dict['experience_cards'] = [cd.to_dict(include_range=False) for cd in player.my_experience_cards]
                
        if what.lower().startswith('degree') or listall:    # list degrees completed
            ndegrees = len(player.my_degrees)
            list_dict['number_of_degrees'] = ndegrees
            if ndegrees > 0:
                list_dict['degrees'] = player.my_degrees
        
        if what.lower().startswith('occ'): # list occupations completed
            noccupations = len(player.occupation_record)
            if noccupations > 0:
                list_dict['occupations_completed'] = noccupations
                list_dict['occupations'] = player.occupation_record
            
        message = json.dumps(list_dict, indent=2, separators=(',', ':'), sort_keys=True)
        result = CommandResult(CommandResult.SUCCESS, message, False)
        return result   

    @staticmethod
    def perform(player:Player, what:str, how:str) -> CommandResult:
        """Perform some pre-defined action.
            Arguments:
                player - Player instance, typically the current player
                what - what to perform, for example "roll"
                how - how to perform it, for example: roll 2 (roll 2 die). The 'how' argument is particular to the 'what' being performed.
            Returns:
                A CommandResult. The message has the result of the operation in JSON format and is dependent on 'what'
                For what == "roll", how = #dice, result message
            If the player has an pending_action that is dependent on a dice roll, that will be automatically resolved
            and the player's status updated accordingly.
            Currently the pending_actions supported are buy_hearts, buy_experience, buy_insurance and gamble.
            
        """
        if what.startswith("roll"):
            # the how has the number of dice (as a string), Player is not used
            ndice = int(how)
            dice = random.choices(population=[1,2,3,4,5,6], k=ndice)
            num_spaces = sum(dice)
            result_dict = {"player" : player.player_initials,  "roll" : num_spaces, "dice" : dice }
            message = json.dumps(result_dict)
            result = CommandResult(CommandResult.SUCCESS, message, False)
        else:
            result = CommandResult(CommandResult.ERROR, f'No such operation: {what}', False)
        
        return result
        
    def execute_opportunity_card(self,  player:Player, opportunityCard:OpportunityCard) -> CommandResult:
            player.opportunity_card = opportunityCard
            message = f'{player.player_initials} Playing  {opportunityCard.opportunity_type}: {opportunityCard.text}'
            self.log(message)
            #
            # Now execute this Opportunity card
            #
            #board_location = player.board_location
            opportunity_type = opportunityCard.opportunity_type   #   OpportunityType enum
            result = CommandResult(CommandResult.SUCCESS, message, False)   #  TODO
            
            if opportunity_type is OpportunityType.OCCUPATION:
                occupation = self.careersGame.get_occupation(opportunityCard.destination)
                if self.can_enter(occupation, player):    # okay to enter, so make it so
                    next_square_number = occupation.entry_square_number
                    next_action = f'goto {next_square_number};roll' 
                    result = CommandResult(CommandResult.EXECUTE_NEXT, f'Advance to  {occupation.name}', False, next_action=next_action)
                else:
                    result = CommandResult(CommandResult.ERROR, f'Cannot use {opportunity_type} to enter {occupation.name}', False)
            
            elif opportunity_type is OpportunityType.OCCUPATION_CHOICE:
                pass
            elif opportunity_type is OpportunityType.BORDER_SQUARE:
                pass
            elif opportunity_type is OpportunityType.BORDER_SQUARE_CHOICE:
                pass
            elif opportunity_type is OpportunityType.ACTION:
                pass
            elif opportunity_type is OpportunityType.TRAVEL:
                pass
            elif opportunity_type is OpportunityType.OPPORTUNITY:
                pass
            else:
                result = CommandResult(CommandResult.ERROR, f'Opportunity type: {opportunity_type} not yet implemented', False)
            
            return result
    
    def save_game(self, gamefile_base_name:str, game_id:str, how='json') -> CommandResult:
        """Save the complete serialized game state so it can be restarted at a later time.
            Arguments:
                how - serialization format to use: 'json', 'jsonpickle' or 'pkl' (pickle)
            NOTE that the game state is automatically saved in pkl format after each player's turn.
            NOTE saving in JSON format saves only the GameState; pkl and jsonpickle persist CareersGame
        """
        extension = 'pkl' if how=='pkl' else 'json'
        filename = f'{gamefile_base_name}.{extension}'      # folder/filename
        if how == 'json':
            jstr = f'{{\n  "game_id" : "{game_id}",\n'
            jstr += f'  "gameState" : '
            jstr += self.game_state.to_JSON()
            jstr += "}\n"

            with open(filename, "w") as fp:
                fp.write(jstr)
            fp.close()
        elif how == 'jsonpickle':
            jstr = self._careersGame.json_pickle()
            with open(filename, "w") as fp:
                fp.write(jstr)
            fp.close()
        else:
            result = joblib.dump(self._careersGame, filename)   # returns a list, as in  ['/data/games/ZenAlien2013_20220909-124721-555368-33134.pkl']
            filename = f'{result}'
        
        self.log(f'game saved to {filename}')
        return CommandResult(CommandResult.SUCCESS, filename, True)

    def log(self, message):
        """Write message to the log file.
            TODO - refactor to use python loging
        """
        msg = GameUtils.get_datetime() + f'  {message}\n'
        if self.fp is not None:     # may be logging isn't initialized yet or logging option is False
            self.fp.write(msg)
        if self.trace:
            print(msg)
    