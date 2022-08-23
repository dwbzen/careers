# ------------------------------------------------------------------------------
# Name:          careersGameEngine.py
# Purpose:       CareersGameEngine class.
#
#                CareersGameEngine executes commands against player-board position
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright (c) 2022 Donald Bacon
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

from game.careersGame import CareersGame
from game.commandResult import CommandResult
from game.player import  Player
from datetime import datetime
import random

class CareersGameEngine(object):
    """CareersGameEngine executes the action(s) associated with each player's turn.
    Valid commands + arguments:
        command :: <roll> | <use> | <retire> | <bump> | <bankrupt> | <list> | <status> | <quit> | <done> | <end game>
                     | <saved games> | <save> | <load> | <query> | <enter> | <goto>
        <use> :: "use"  <card-type>
        <card_type> :: "opportunity" | "experience" 
        <roll> :: "roll"                        ;roll 1 or 2 dice depending on where the player is on the board
        <retire> :: "retire"                    ;immediate go to retirement square (Spring Break, Holiday)
        <bump> :: "bump" player_initials        ;bump another player, who must be on the same square as the bumper
        <bankrupt> :: "bankrupt"                ;declare bankruptcy
        <list> :: "list"  <card_type> | "occupations"           ;list my opportunities or experience cards, or occupations completed
        <status> :: "status"                    ;display my cash, #hearts, #stars, salary, total points, and success formula
        <quit> :: "quit" player_initials        ;current player leaves the game, must include initials
        <done> :: "done" | "next"               ;done with my turn - next player's turn
        <end game> :: "end game"                ;saves the current game state then ends the game
        <saved games> :: "saved games"          ;list any saved games by date/time and gameID
        <save> :: "save"                        ;saves the current game state to a file as JSON
        <load> :: "load" game-id                ;load a game and start play with the next player
        <query> :: "where" <who>                ;gets info on a player's current location on the board
        <who> :: "am I" | "is" <playerID>
        <playerID> :: player_name | player_initials
        <enter> :: "enter" <occupation_name> [<square_number>]        ;enter occupation at occupation square square_number
        <goto> :: "goto" <square_number>                              ;go to border square square_number
    """
    
    COMMANDS = ['roll', 'use', 'goto', 'enter', 'status', 'done', 'next', 'end', 'quit', 'save', 'where', \
                'retire', 'bump', 'bankrupt', 'list', 'saved', 'load',  'who']
    
    def __init__(self, careersGame:CareersGame):
        '''
        Constructor
        '''
        self._careersGame = careersGame
        self._game_state = self._careersGame.game_state
        self._trace = True         # traces the action by describing each step and logs to a file
        self._logfile_name = "careersLog_" + careersGame.edition_name
        self._logfile_path = "/data/log"    # TODO put in Environment
        self._fp = None     # log file open channel
        self._start_date_time = datetime.now()
        self._gameId = careersGame.gameId
        
        self._current_player = None
    
    @property
    def fp(self):
        return self._fp
    
    @fp.setter
    def fp(self, value):
        self._fp = value
    
    @property
    def logfile_name(self):
        return self._logfile_name
    
    @property
    def logfile_path(self):
        return self._logfile_path
    
    @property
    def gameId(self):
        return self._gameId
    
    @property
    def trace(self):
        return self._trace
    
    @trace.setter
    def trace(self, value):
        self._trace = value
        
    @property
    def game_state(self):
        return self._game_state
    
    def get_datetime(self) -> str:
        now = datetime.today()
        return '{0:d}{1:02d}{2:02d}_{3:02d}{4:02d}'.format(now.year, now.month, now.day, now.hour, now.minute)
    
    def log(self, message):
        msg = self.get_datetime() + f'  {message}\n'
        self.fp.write(msg)
        if self.trace:
            print(msg)
    
    def start(self):
        self.fp = open(self.logfile_path + "/" + self.logfile_name + "_" + self.gameId + ".log", "w")
        self.log("Starting game: " + self.gameId)

    def execute_command(self, command:str, player:Player, args:list=[]):
        """Executes a command for a given Player
            Arguments:
                command - the command name, for example "roll"
                args - a possibly empty list of additional string arguments
                player - a Player reference
            Returns: result dictionary with the keys:
                "result" - 0 = success, 1 = error, 2 = game is over
                "message" - the result message to be communicated to the player.
                "done" - if True, the move is complete. Otherwise more is required from the Player
        
        """
        
        self.log(f'{player.player_initials}: {command} {args}')
        if command is None or len(command) == 0:
            return CommandResult(0, "", False)
        cmd_result = self._evaluate(command, args)
        self.log(f'  {player.player_initials} results: {cmd_result.return_code} {cmd_result.message}')
        return cmd_result
        
    def _evaluate(self, commandTxt, args=[]):
        command_result = self._parse_command_string(commandTxt, args)
        if command_result.return_code != 0: # must be an error
            return command_result
        
        command = "self." + command_result.message
        command_result = None
        print("execute " + command)
        try:
            command_result = eval(command)
        except Exception as ex:
            command_result = CommandResult(1,  "Invalid command syntax",  False, exception=ex)
        return command_result
        
    def _parse_command_string(self, txt, addl_args=[]):
        """Parses a command string into a string that can be evaluated with eval()
            Returns: if return_code == 0, a CommandResult with commandResult.message as the string to eval()
                else if return_code == 1, commandResult.message has the error message
        """
        command_args = txt.split()
            
        command = command_args[0]
        if not command in CareersGameEngine.COMMANDS:
            return CommandResult(1,  "Invalid command: "+ '"command"',  False)
        if len(command_args) > 1:
            args = command_args[1:]
            command = command + "("
            for arg in args:
                if arg.isdigit():
                    command = command + arg + ","
                else:
                    command = command + f'"{arg}",'
        
            command = command[:-1] 
        else:
            command = command + "("
            
        if addl_args is not None and len(addl_args) > 0:
            for arg in addl_args:
                command = command + f'"{arg}",'
            command = command[:-1]
        command += ")"   
        return CommandResult(0, command, False)
    
    def get_player_game_square(self, player):
        current_border_square_number, current_occupation_name, current_occupation_square_number = player.get_current_location()
        game_square = None
        if current_occupation_name is not None:    # get the Occupation square
            occupation = self._careersGame.occupations[current_occupation_name]    # Occupation instance
            game_square = occupation.occupationSquares[current_occupation_square_number]
        else:       # get the border square
            game_square = self._careersGame.game_board[current_border_square_number]
        
        return game_square
    
    def get_player(self, pid):
        """Gets a Player by initials or name
        
        """
        player = None
        players = self.game_state.players
        lc_pid = pid.lower()
        for p in players:
            if p.player_initials.lower() == lc_pid or p.player_name.lower() == lc_pid:
                player = p
                break
        return player
    
    ############
    #
    # command implementations
    # 
    ##########
    def roll(self, number_of_dice=2):
        """Roll 1 or 2 dice and advance that number of squares for current_player and execute the occupation or border square.
        """
        done = False
        player = self.game_state.current_player
        game_square = self.get_player_game_square(player)
        border_square_number, occupation_name, occupation_square_number = player.get_current_location()
        
        dice = random.choices(population=[1,2,3,4,5,6], k=number_of_dice)
        total = sum(dice)
        
        message = f' {player.player_initials}  rolled {total} {dice}'
        result = CommandResult(0, message, done)
        return result
    
    def use(self, what):
        """Use an Experience or Opportunity card in place of rolling the die
        
        """
        result = CommandResult(0, "Command not yet implemented", False)
        return result
        
    def goto(self, square_number):
        """Immediately place the current player on the designated border square execute that border square.
            
        """
        if square_number >= 0 and square_number <= self._careersGame.game_layout_dimensions['size']:
            player = self.game_state.current_player
            player.current_border_square_number = square_number
            player.current_occupation_name = None
            return self.where("am","I")
        else:
            return CommandResult(1, "No such border square", False)
    
    def enter(self, occupation_name, square_number=0):
        """Enter the named occupation at the designated square number and execute the occupation square.
        
        """
        if occupation_name in self._careersGame.occupation_names:
            player = self.game_state.current_player
            player.current_occupation_name = occupation_name
            player.current_occupation_square_number = square_number
            # TODO - execute the contents of the occupation square
            return self.where("am","I")
        else:
            return CommandResult(1, "No such occupation", False)
    
    def status(self):
        player = self.game_state.current_player
        message = player.player_info(include_successFormula=True)
        result = CommandResult(0,  message, False)
        return result       
    
    def done(self):
        """End my turn and go to the next player
        """
        result = CommandResult(0,  "Turn is complete" , True)
        return result
    
    def next(self):
        """Synonym for done - go to the next player
        """
        return self.done()
    
    def end(self, save=None):
        """Ends the game and exits.
        """
        self.log("Ending game: " + self.gameId)
        if save is not None and save.lower()=='save':    # save the game state first
            sg_result = self.save_game()
            result = CommandResult(2, f'Game is complete and saved to file: {sg_result.message}', True)
        else:
            result = CommandResult(2, "Game is complete" , True)

        return result
    
    def quit(self, initials):
        """A single player, identified by initials, leaves the game.
        """
        result = CommandResult(0, "Command not yet implemented", False)
        return result
    
    def save(self):
        """Save the current game state
        """
        return self.save_game()
    
    def where(self, t1:str="am", t2:str="I"):
        """where am I or where is <player>
        """
        player = None 
        
        result = 0
        if t1=='am' and t2.lower() == 'i':
            player = self.game_state.current_player
            message = "You are on square# "
        elif t1=='is':
            # t2 is a player's initials or name
            message = f'{t2} is on square# '
            player = self.get_player(t2)
        if player is not None:
            border_square_number, occupation_name, occupation_board_number = player.get_current_location()
            game_square = self.get_player_game_square(player)
            message += str(game_square.number)
            if game_square.square_class == 'Occupation':
                message += " of " + occupation_name + ": '" +  game_square.text + "' " + game_square.action_text
            else:    # a border square
                message += ": " + game_square.name
        else:
            message = f'No such player: {t2}'
            result = 1
        
        return CommandResult(result, message, False)
        
    #####################################
    #
    # Game engine action implementations
    #
    #####################################
    
    def save_game(self):
        jstr = f'{{\n  "game_id" : "{self.gameId}",\n'
        jstr += f'  "gameState" : {{\n'
        jstr += self.game_state.to_JSON()
        jstr += "\n  }\n}"
        
        self.log(jstr)
        filename = self._logfile_path + "/" + self.gameId + "_saved.json"
        with open(filename, "w") as fp:
            fp.write(jstr)
        fp.close()
        return CommandResult(0, filename, True)
        
        