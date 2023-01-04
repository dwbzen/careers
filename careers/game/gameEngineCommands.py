'''
Created on Sep 11, 2022

@author: don_bacon
'''

from game.careersGame import CareersGame
from game.commandResult import CommandResult
from game.player import Player
from game.gameUtils import GameUtils
from game.opportunityCard import OpportunityCard, OpportunityType, OpportunityActionType
from game.occupation import Occupation
from game.gameConstants import GameConstants, PendingActionType

from typing import Tuple, List
import joblib
import random, json
from game.borderSquare import BorderSquareType

class GameEngineCommands(object):
    """Implementations of CareersGameEngine commands.
    
    """
    
    def __init__(self, thegame:CareersGame, logfile_pointer):
        self._careersGame = thegame
        self._game_state = self._careersGame.game_state
        self.fp = logfile_pointer
        self._debug = False          # traces the action by describing each step and logs to a file
        self.currency_symbol = self._careersGame.game_parameters.get_param("currency_symbol")
    
    @property 
    def careersGame(self) -> CareersGame:
        return self._careersGame
    
    @careersGame.setter
    def careersGame(self, thegame:CareersGame):
        self._careersGame = thegame
        
    @property
    def debug(self):
        return self._debug
    
    @debug.setter
    def debug(self, value):
        self._debug = value
        
    def can_player_move(self, player:Player, dice:List[int] | None) -> Tuple[bool,CommandResult] :
        """Determine if a Player can move.
            A player cannot move if bankrupt (cash < 0) and can move from the Hospital or Unemployment
            only if the rolled dice meet the requirements for that game square.
            Arguments:
                player - the current Player
                dice - the player's roll as a List[int], for example [6,5] (I rolled an 11!)
                       If None, return True
            Returns: a 2-element tupple consisting of a boolean (the player can move or not)
            and a CommandResult.
        """
        if dice is None:
            result = CommandResult(CommandResult.SUCCESS, f'Player may move', True)
        else:
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
                [3] an error message if player cannot enter (blank string if player can enter)
        """
        message = ""
        entry_fee = occupation.entry_fee
        has_fee = player.cash >= entry_fee
        occupationClass = occupation.occupationClass
        # anyone can go to college if they have the funds
        if occupationClass == 'college':
            # check if any outstanding SELECT_DEGREE pending actions
            # Need to resolve before entering
            if player.has_pending_action(PendingActionType.SELECT_DEGREE):
                message = f'You need to resolve {PendingActionType.SELECT_DEGREE.value} before entering College'
                return (False, entry_fee, message)
            if has_fee:
                return (True, entry_fee, message)    # always pay for college
            else:    # Can't afford College
                message = f"Sorry, you don't meet the conditions for entering {occupation.name}, entry fee: {entry_fee}"
                return (False, entry_fee, message)
        
        #
        # check occupation record for prior trips through 
        #
        if occupation.name in player.occupation_record and player.occupation_record[occupation.name] > 0:
            return (True, 0, message)
        #
        # check degree requirements
        #
        degreeRequirements = occupation.degreeRequirements
        degreeName = degreeRequirements['degreeName']
        numberRequired = degreeRequirements['numberRequired']
        if degreeName in player.my_degrees and player.my_degrees[degreeName] >= numberRequired:
            return (True, 0, message)        # can enter for free
        #
        # is the player using a  "All expenses paid" Opportunity card ?
        #
        if player.opportunity_card is not None:
            if player.opportunity_card.expenses_paid:
                return (True, 0, message)
        
        return has_fee, entry_fee, message

    def can_backstab_player(self, player:Player, other_player:Player, occupation:Occupation) ->bool:
        '''Determine if this player can back stab another player in a given Occupation.
            Rule (1) player is currently on the Occupation path, AND
                 (2) other_player must have completed the Occupation, OR
                 (3) other_player is currently on the Occupation path
        '''
        can_do = occupation.name in other_player.occupation_record
        if not can_do:
            can_do = other_player.board_location.occupation_name is not None and other_player.board_location.occupation_name==occupation.name
        can_do = can_do or occupation.name in player.occupation_record
        return can_do
    

    @staticmethod
    def parse_command_string(txt:str, addl_args=[]) -> CommandResult:
        """Parses a command string into an executable string, i.e. that can be evaluated with eval()
            Returns: if return_code == 0, a CommandResult with commandResult.message as the string to eval()
                else if return_code == 1, commandResult.message has the error message
        """
        command_args = txt.split()
            
        command = command_args[0]
        cmd_arg = None if len(command_args) < 2 else command_args[1].lower()
        if not command in GameConstants.COMMANDS:
            return CommandResult(CommandResult.ERROR,  f'Invalid command: "{command}"',  False)
        if len(command_args) > 1:
            args = command_args[1:]
            if command.lower() == "resolve":
                kwargs = '"' if len(command_args) >= 3 else '""'
                for s in command_args[2:]:
                        kwargs += f'{s} '
                match(cmd_arg):
                    case "backstab":    # backstab + at least 1 player initials
                        #
                        # resolve backstab takes kwargs['player_initials']
                        #
                        command = f'resolve("backstab","",player_initials={kwargs[:-1]}" )'
                                       
                    case "*":
                        command = f'resolve("*",{kwargs[:-1]}" )'
                    
                    case _:
                        command = f'resolve("{cmd_arg}",{kwargs[:-1]}" )'
                                         
                return CommandResult(CommandResult.SUCCESS, command, True)
                    
            else:
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
            # add the choice argument for resolve command as '1'
            command += f',"1")'
        else:
            command += ")"
        
        return CommandResult(CommandResult.SUCCESS, command, False)
    
    @staticmethod
    def list(player:Player, what:str, how:str) ->CommandResult:
        """List the Experience or Opportunity cards held by the current player
            Arguments: 
                what - 'experience', 'opportunity', or 'all'
                how - display control: 'full', 'condensed' or 'count'
            Returns: CommandResult.message is the stringified list of str(card).
                For Opportunity cards this is the text property.
                For Experience cards this is the number of spaces (if type is fixed), otherwise the type.
            
        """
        list_dict = player.list(what, how)
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
            result = CommandResult(CommandResult.ERROR, f'Operation: {what} is not supported', False)
        
        return result
        
    def execute_opportunity_card(self,  player:Player, opportunityCard:OpportunityCard, dest:str|int|None=None) -> CommandResult:
        """Executes a given OpportunityCard for a Player
            Arguments:
                player - the current Player
                opportunityCard - a OpportunityCard instance
                dest - optional destination choice as a game square name, for example 'Amazon' or 'Payday'
                       If used, a pending_action to resolve the border or occupation square is not set.
        
        """
        player.opportunity_card = opportunityCard
        message = f'{player.player_initials} Playing  {opportunityCard.opportunity_type}: {opportunityCard.text}'
        self.log(message)
        #
        # Now execute this Opportunity card
        #
        #board_location = player.board_location
        opportunity_type = opportunityCard.opportunity_type   #   OpportunityType enum
        result =  CommandResult(CommandResult.ERROR, f'Opportunity type: {opportunity_type} not yet implemented', False)
        
        if opportunity_type is OpportunityType.OCCUPATION:
            occupation = self.careersGame.get_occupation(opportunityCard.destination)
            if self.can_enter(occupation, player):    # okay to enter, so make it so
                next_square_number = occupation.entry_square_number
                next_action = f'goto {next_square_number};roll' 
                result = CommandResult(CommandResult.EXECUTE_NEXT, f'Advance to  {occupation.name}', False, next_action=next_action)
            else:
                result = CommandResult(CommandResult.ERROR, f'Cannot use {opportunity_type} to enter {occupation.name} now.', False)
        
        elif opportunity_type is OpportunityType.OCCUPATION_CHOICE:    # choose_occupation
            if dest is None:
                player.add_pending_action(PendingActionType.CHOOSE_OCCUPATION)
                message = f'{opportunityCard.text}\n{opportunityCard.pending_action}'
                result = CommandResult(CommandResult.NEED_PLAYER_CHOICE, message, False)
            else:
                occupation = self.careersGame.get_occupation(dest)
                if self.can_enter(occupation, player):    # okay to enter, so make it so
                    next_square_number = occupation.entry_square_number
                    next_action = f'goto {next_square_number};roll' 
                    result = CommandResult(CommandResult.EXECUTE_NEXT, f'Advance to  {occupation.name}', False, next_action=next_action)
                else:
                    result = CommandResult(CommandResult.ERROR, f'Cannot use {opportunity_type} to enter {occupation.name} now.', False)     
            
        elif opportunity_type is OpportunityType.BORDER_SQUARE:    # border_square
            #
            # advance to the designated border square and execute it
            #
            game_square = self.careersGame.find_border_square(opportunityCard.destination)
            next_square_number = game_square.number
            next_action = f'goto {next_square_number}'
            result = CommandResult(CommandResult.EXECUTE_NEXT, f'Advance to  {opportunityCard.destination}', False, next_action=next_action)                
            
        elif opportunity_type is OpportunityType.BORDER_SQUARE_CHOICE:    # choose_destination
            if dest is None:
                player.add_pending_action(PendingActionType.CHOOSE_DESTINATION)
                message = f'{opportunityCard.text}\n{opportunityCard.pending_action}'
                result = CommandResult(CommandResult.NEED_PLAYER_CHOICE, message, False)
            else:
                game_square = self.careersGame.find_border_square(dest)
                next_square_number = game_square.number
                next_action = f'goto {next_square_number}'
                result = CommandResult(CommandResult.EXECUTE_NEXT, f'Advance to  {dest}', False, next_action=next_action)
            
        elif opportunity_type is OpportunityType.ACTION:
            #
            # depends on action_type: leave_unemployment, extra_turn, collect_experience
            action_type = opportunityCard.action_type
            if action_type is OpportunityActionType.COLLECT_EXPERIENCE:
                #
                # collect a randomly selected Experience card from all other players (holding experience cards)
                #
                message = ""
                for aplayer in self.careersGame.game_state.players:
                    ncards = len(aplayer.my_experience_cards)
                    if player.number != aplayer.number and ncards > 0:
                        ind = random.randint(0, ncards-1)    # the index of the card to move to this player
                        thecard = aplayer.my_experience_cards[ind]
                        aplayer.remove_experience_card(thecard)
                        player.add_experience_card(thecard)
                        message += f'Experience card {thecard.card_type.value} moved from player {aplayer.player_initials} to {player.player_initials}\n'
                if len(message) == 0:
                    message = "Sadly, no other player has Experience to move."
                result = CommandResult(CommandResult.SUCCESS, message, True)
            
            elif action_type is OpportunityActionType.LEAVE_UNEMPLOYMENT:
                player.is_unemployed = False
                result = CommandResult(CommandResult.SUCCESS, f'{player.player_initials} may leave Unemployment' , False)
            
            elif action_type is OpportunityActionType.EXTRA_TURN:
                player.extra_turn = player.extra_turn + 1    # give the player 1 extra turn
                result = CommandResult(CommandResult.SUCCESS, f'{player.player_initials} may take an extra turn!', False)
            
            else:
                result = CommandResult(CommandResult.SUCCESS, f'{action_type.value} not yet implemented', True)
            
        elif opportunity_type is OpportunityType.TRAVEL:
            #
            # advance to the nearest travel square and roll again
            #
            current_square_number = player.board_location.border_square_number
            next_square_number, next_square = self.careersGame.find_next_border_square(current_square_number, BorderSquareType.TRAVEL_SQUARE)
            next_action = f'goto {next_square_number}'
            result = CommandResult(CommandResult.EXECUTE_NEXT, f'Advance to position {next_square_number}:  {next_square.name}', False, next_action=next_action)
                            
        elif opportunity_type is OpportunityType.OPPORTUNITY:
            #
            # advance to the Opportunity square closest to the player's current position
            # and roll again
            #
            current_square_number = player.board_location.border_square_number
            next_square_number, next_square = self.careersGame.find_next_border_square(current_square_number, BorderSquareType.OPPORTUNITY_SQUARE)
            next_action = f'goto {next_square_number}'
            result = CommandResult(CommandResult.EXECUTE_NEXT, f'Advance to position {next_square_number}:  {next_square.name}', False, next_action=next_action)
            
        else:
            result = CommandResult(CommandResult.ERROR, f'No such Opportunity type: {opportunity_type}', False)
        
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
            jstr += self._careersGame.game_state.to_JSON()
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
        if self.debug:
            print(msg)
    