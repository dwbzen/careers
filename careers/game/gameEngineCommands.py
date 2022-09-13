'''
Created on Sep 11, 2022

@author: don_bacon
'''

from game.careersGame import CareersGame
from game.commandResult import CommandResult
from game.player import Player
from game.gameUtils import GameUtils
import joblib

class GameEngineCommands(object):
    """Implementations of CareersGameEngine commands.
    
    """
    COMMANDS = ['add', 'bankrupt', 'bump', 'buy', 'create', 'done', 'end', 'enter', 
                'game_status', 'goto', 'list', 'load', 'next', 'pay', 'quit', 'retire', 
                'roll', 'save', 'saved', 'start', 'status', 'transfer', 'use', 'use_insurance', 
                'where', 'who']
    

    def __init__(self, thegame:CareersGame, logfile_pointer):
        self._careersGame = thegame
        self._game_state = self._careersGame.game_state
        self.fp = logfile_pointer
        self._trace = True          # traces the action by describing each step and logs to a file
    
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
        
    def can_player_move(self, player:Player) -> tuple[bool,CommandResult] :
        """Determine if a Player can move from the Hospital or Unemployment
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
            result = game_square.execute_special_processing(player)
        else:
            result = CommandResult(CommandResult.SUCCESS, "", True)
            
        can_move = result.is_successful()
        return can_move, result

    @staticmethod
    def parse_command_string(txt, addl_args=[]) -> CommandResult:
        """Parses a command string into a string that can be evaluated with eval()
            Returns: if return_code == 0, a CommandResult with commandResult.message as the string to eval()
                else if return_code == 1, commandResult.message has the error message
        """
        command_args = txt.split()
            
        command = command_args[0]
        if not command in GameEngineCommands.COMMANDS:
            return CommandResult(CommandResult.ERROR,  f'Invalid command: {command}',  False)
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
        message = ""
        listall = (what.lower() == 'all')

        if what.lower().startswith('opportun') or listall:
            if len(player.my_opportunity_cards) == 0:
                message += "No Opportunity cards\n"
            else:
                n = 1
                for card in player.my_opportunity_cards:
                    num = card.number
                    message += f'{n}.  {num}: {str(card)}\n'
                    n += 1
                    
        if what.lower().startswith('exp') or listall:
            if len(player.my_experience_cards) == 0:
                message += "\nNo Experience cards"
            else:
                n = 1
                for card in player.my_experience_cards:
                    message += f'{n}.  {num}: {str(card)}\n'
                    n+= 1
            
        result = CommandResult(CommandResult.SUCCESS, message, False)
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
    