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
from game.opportunityCard import OpportunityCard
from game.experienceCard import ExperienceCard
from game.boardLocation import BoardLocation
from game.successFormula import SuccessFormula
from game.borderSquare import BorderSquare
from game.occupationSquare import OccupationSquare
from game.gameSquare import GameSquare
from game.gameEngineCommands import GameEngineCommands
from game.gameUtils import GameUtils

from datetime import datetime
import random
from typing import Optional, List


class CareersGameEngine(object):
    """CareersGameEngine executes the action(s) associated with each player's turn.
    Valid commands + arguments:
        command :: <roll> | <use> | <retire> | <bump> | <bankrupt> | <list> | <status> | <quit> | <done> | <end game> |
                   <saved games> | <save> | <load> | <query> | <enter> | <goto> | <add> | <use insurance> | <add degree> |
                   <pay> | <transfer> | <game_status> | <create> | <start> | <buy>
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
        <save> :: "save" <how>                  ;saves the current game state to a file in the specified format
        <how> ::  "json" | "pkl"
        <load> :: "load" game-id                ;load a game and start play with the next player
        <query> :: "where" <who>                ;gets info on a player's current location on the board
        <who> :: "am I" | "is" <playerID>
        <playerID> :: player_name | player_initials
        <enter> :: "enter" <occupation_name> [<square_number>]                 ;enter occupation at occupation square square_number
        <goto> :: "goto" <square_number>                                       ;go to border square square_number
        <add> :: "add player" player_name player_initials cash stars hearts    ;adds a new player to the game
        <use insurance> :: "use_insurance"
        <add degree> :: "add degree" <degree program>
        <degree program> :: See collegeDegrees-<edition name>.json "degreePrograms"
        <pay> :: "pay" amount                ;current player makes a payment associated with their current board location
        <transfer> :: "transfer" quantity ("cash" | "opportunity" | "experience) player_number
        <game_status> :: "game_status"
        <create> :: "create" <edition> <game_type> points  [id]      ;create a new CareersGame with specified total points or total time (in minutes) and optional gameId
        <edition> :: "Hi-Tech"    ;supports multiple editions
        <game_type> ::  'points' | 'timed'
        <start> :: "start"                    ;starts a newly created CareersGame
        <buy>  :: "buy"  ( "hearts" | "stars" | "experience" | "opportunity" ) quantity cash_amount  ;buy some number of items for the cash_amount provided
    """
    
    
    def __init__(self):
        '''
        Constructor
        '''
        self._fp = None             # logging file pointer
        self._careersGame = None    # create a new CareersGame with create()
        self._trace = True          # traces the action by describing each step and logs to a file
        self._start_date_time = datetime.now()
        self._gameId = None
        self._master_id = None      # provided by the UI
        self._current_player = None
        self._admin_player = Player(number=-1, name='Administrator', initials='admin')
        self._gameEngineCommands = None     # no CareersGame yet
    
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
    def master_id(self):
        return self._master_id
    
    @property
    def trace(self):
        return self._trace
    
    @trace.setter
    def trace(self, value):
        self._trace = value
        
    @property
    def game_state(self):
        return self._game_state
    
    @property
    def careersGame(self):
        return self._careersGame
    
    def log(self, message):
        """Write message to the log file.
            TODO - refactor to use python loging
        """
        msg = GameUtils.get_datetime() + f'  {message}\n'
        if self.fp is not None:     # may be logging isn't initialized yet or logging option is False
            self.fp.write(msg)
        if self.trace:
            print(msg)

    def execute_command(self, command:str, aplayer:Player, args:list=[]) -> CommandResult:
        """Executes command(s) for a given Player
            Arguments:
                command - the command name, for example "roll". Multiple commands are separated by a semicolon.
                args - a possibly empty list of additional string arguments
                player - a Player reference. If none, admin_player is used.
            Returns: a CommandResult object. The player's current board_location is always returned in the CommandResult
            See game.CommandResult for details
        
        """
        player = aplayer
        if aplayer is None:
            player = self._admin_player
        
        commands = command.split(';')
        messages = ""
        for command in commands:
            self.log(f'{player.player_initials}: {command}')
            if command is None or len(command) == 0:
                return CommandResult(CommandResult.SUCCESS, "", False)
            cmd_result = self._evaluate(command, args)
            
            board_location = player.board_location    # current board location AFTER the command is executed
            self.log(f'  {player.player_initials} results: {cmd_result.return_code} {cmd_result.message}\n{board_location}')
            cmd_result.board_location = board_location
            messages += cmd_result.message + "\n"
        
        cmd_result.message = messages
        return cmd_result
        
    def _evaluate(self, commandTxt, args=[]) -> CommandResult:
        """Evaulates a command string with eval()
            Arguments:
                commandTxt - the command name + any arguments to evaluate.
                args - an optional list of additional arguments
            Returns - a CommandResult
        """
        command_result = GameEngineCommands.parse_command_string(commandTxt, args)
        if command_result.return_code != CommandResult.SUCCESS:     # must be an error
            return command_result
        
        command = "self." + command_result.message
        command_result = None
        print("execute " + command)
        try:
            command_result = eval(command)
        except Exception as ex:
            command_result = CommandResult(CommandResult.ERROR,  f'"{command}" : Invalid command format or syntax\n{str(ex)}',  False, exception=ex)
            #raise ex
        return command_result
        
    def _parse_command_string(self, txt, addl_args=[]) -> CommandResult:
        """Parses a command string into a string that can be evaluated with eval()
            Returns: if return_code == 0, a CommandResult with commandResult.message as the string to eval()
                else if return_code == 1, commandResult.message has the error message
        """
        command_args = txt.split()
            
        command = command_args[0]
        if not command in CareersGameEngine.COMMANDS:
            return CommandResult(1,  f'Invalid command: {command}',  False)
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
        
        return CommandResult(0, command, False)
    
    def get_player_game_square(self, player:Player) -> GameSquare:
        board_location = player.board_location
        game_square = None
        if board_location.occupation_name is not None:    # get the Occupation square
            occupation = self._careersGame.occupations[board_location.occupation_name]    # Occupation instance
            game_square = occupation.occupationSquares[board_location.occupation_square_number]
        else:       # get the border square
            game_square = self._careersGame.get_border_square(board_location.border_square_number)
        
        return game_square
    
    def get_player(self, pid, pnumber=None) -> Optional[Player] :
        """Gets a Player by initials, name, or number
            Returns: Player instance or None if no player with the given ID exists.
        """
        player = None
        if pnumber is not None:
            player = self.game_state.players[pnumber]
        else:   # lookup the player by name or initials
            players = self.game_state.players
            lc_pid = pid.lower()
            for p in players:
                if p.player_initials.lower() == lc_pid or p.player_name.lower() == lc_pid:
                    player = p
                    break
        return player
    
    #############################################################################
    #
    # command implementations. All command implementations return a CommandResult
    # Each command corresponds to a specific web server endpoint
    # 
    #############################################################################
    def roll(self, number_of_dice=2) ->CommandResult:
        """Roll 1 or 2 dice and advance that number of squares for current_player and execute the occupation or border square.
        """
        player = self.game_state.current_player
        ndice = number_of_dice
        game_square = self.get_player_game_square(player)       # could be BorderSquare or OccupationSquare

        if game_square.square_class == 'occupation':    # then I am on an occupation path so roll 1 die
            ndice = 1
        
        dice = random.choices(population=[1,2,3,4,5,6], k=ndice)
        num_spaces = sum(dice)
        
        #
        # check if the player is Unemployed and if so, if the roll allows them to move
        #
        canmove, result = self._gameEngineCommands.can_player_move(player)
        
        if canmove:
            next_square_number = self._get_next_square_number(player, num_spaces)
            
            self.log(f' {player.player_initials}  rolled {num_spaces} {dice}')
    
            #
            # place the player on the next_square_number
            #
            result = self.goto(next_square_number)
        return result
    
    def use(self, what, card_number, spaces=0) -> CommandResult:
        """Use an Experience or Opportunity card in place of rolling the die.
            Experience and Opportunity cards are identified (through the UI) by number, which uniquely
            identifies the card function. i.e. Cards having the same "number" are identical
            with respect to the end result. There are generally more than 1 card of a given number
            in the deck and this is identified by the ordinal "ncard".
            Arguments:
                what - "opportunity", "experience"
                card_number - the unique number for this card. Corresponds to card.number
                spaces - required for Experience wild cards.
        """
        player = self.game_state.current_player

        result = None
        #
        # get the actual card instance from the players deck
        #
        if what.lower() == 'opportunity':
            cards = player.get_opportunity_cards()   # dict with number as the key
            thecard_dict = cards.get(card_number, None)
            if thecard_dict is None:    # no such card
                result = CommandResult(CommandResult.ERROR, f"No {what} card exists with number {card_number} ", False)
            else:
                thecard = thecard_dict['card']
                player.opportunity_card = thecard
                result = self._execute_opportunity_card(player, opportunityCard=thecard)
        elif what.lower() == 'experience':
            cards = player.get_experience_cards()   # dict with number as the key
            thecard_dict = cards.get(card_number, None)
            if thecard is None:    # no such card
                result = CommandResult(CommandResult.ERROR, f"No {what} card exists with number {card_number} ", False)
            else:
                thecard = thecard_dict['card']
                player.experience_card = thecard
                result = self._execute_experience_card(player, experienceCard=thecard, spaces=spaces)
        else:
            result = CommandResult(CommandResult.ERROR, f"use can't use a '{what}' ", False)
            
        return result
    
    def use_insurance(self) -> CommandResult:
        """Use insurance, if you have it, to avoid paying a penalty or loosing hearts/stars/salary
            Returns: CommandMessage with return_code == SUCCESSFUL if okay, == ERROR if no insurance
                or not applicable in this case.
        """
        player = self.game_state.current_player
        if player.is_insured:
            result = CommandResult(CommandResult.SUCCESS, "'use_insurance' command not yet implemented", False)
        else:
            result = CommandResult(CommandResult.ERROR, "You don't have insurance!", False)
        return result
        
    def goto(self, square_number:int) -> CommandResult:
        """Immediately place the designated player on the designated BorderSquare OR OccupationSquare and execute that square.
            If the current player is in an occupation, this places the player on square_number of that Occupation.
            Otherwise, the square_number refers to a BorderSquare.
            NOTE that the border square number could be out of range. i.e. > game size. 
            If so, the square number adjusted and then the pass_payday() action is executed.
            
            NOTE that when in an Occupation the designated square_number could be out of range. i.e. > the occupation exit_square_number.
            If so, the player is advanced to the next BorderSquare and the exit occupation logic is executed.
            
        """
        return self._goto(square_number, self.game_state.current_player)
    
    def enter(self, occupation_name:str) -> CommandResult:
        """Enter the named occupation at the designated square number and execute the occupation square.
            This checks if the player meets the entry conditions
            and if not, return an error with the appropriate message.
            Upon entering, the player's BoardLocation  occupation_name is set to occupation_name,
            and border_square_number = current border_square_number.
            Arguments:
                occupation_name - the name of the occupation to enter. Case-sensitive!
            Return:
                CommandResult
                
            The player must either roll or use an experience card to actually enter the Occupation.
        """
        player = self.game_state.current_player
        if occupation_name in self._careersGame.occupation_names:
            occupation_entrance_square = self._careersGame.get_occupation_entrance_squares()[occupation_name]    # BorderSquare instance
            #
            # if player used an Opportunity to get here, remove that from their deck and set their opportunity_card to None
            #
            if player.opportunity_card is not None and player.opportunity_card.opportunity_type=='occupation' and player.opportunity_card == occupation_name:
                player.used_opportunity()
                    
            if self.can_enter(occupation_name, player):        # this also checks the Opportunity card used (if any)
                player.board_location.border_square_number = occupation_entrance_square.number
                player.board_location.border_square_name=occupation_entrance_square.name
                player.board_location.occupation_name=occupation_name
                player.board_location.occupation_square_number = -1     # still need to roll or use a card

                result = self.where("am","I")
                return CommandResult(result.return_code, f'{result.message}', True)
            else:
                return CommandResult(CommandResult.ERROR, "Sorry, you don't meet the occupations entry conditions.", False)
        else:
            return CommandResult(CommandResult.ERROR, "No such occupation", False)
    
    def status(self, initials:str=None) -> CommandResult:
        player = self.game_state.current_player if initials is None else self.get_player(initials)
        message = player.player_info(include_successFormula=True)
        result = CommandResult(CommandResult.SUCCESS,  message, False)
        return result       
    
    def done(self) -> CommandResult:
        """End my turn and go to the next player
        """
        cp = self.game_state.current_player
        cp.board_location.reset_prior()            # this player's prior board position no longer relevant
        npn = self.game_state.set_next_player()    # sets current_player and returns the next player number (npn) and increments turns
        player = self.game_state.current_player
        player.opportunity_card = None
        player.experience_card = None
        #
        # save the Game on change of turns
        #
        self._gameEngineCommands.save_game(self._game_filename_base, self.gameId, how='pkl')
        result = CommandResult(CommandResult.SUCCESS,  f"{cp.player_initials} Turn is complete, {player.player_initials}'s ({npn}) turn " , True)
        return result
    
    def next(self) -> CommandResult:
        """Synonym for done - go to the next player
        """
        return self.done()
    
    def end(self, save:str=None) -> CommandResult:
        """Ends the game, saves the current state if specified, and exits.
        """
        self.log("Ending game: " + self.gameId)
        if save is not None and save.lower()=='save':    # save the game state first
            sg_result = self.save_game()
            result = CommandResult(CommandResult.TERMINATE, f'Game is complete and saved to file: {sg_result.message}', True)
        else:
            result = CommandResult(CommandResult.TERMINATE, "Game is complete" , True)

        return result
    
    def quit(self, initials:str) -> CommandResult:
        """A single player, identified by initials, leaves the game.
        """
        result = CommandResult(CommandResult.SUCCESS, "'quit' command not yet implemented", False)
        return result
    
    def save(self, how="pkl") -> CommandResult:
        """Save the current game state.
            Arguments: how - save format: 'json' or 'pkl' (the default).
            save('pkl') uses joblib.dump() to save the CareersGame instance to binary pickel format.
            This can be reconstituted with joblib.load()
        """
        return self._gameEngineCommands.save_game(self._game_filename_base, self.gameId, how=how)
    
    def where(self, t1:str="am", t2:str="I") -> CommandResult:
        """where am I or where is <player>
        """
        player = None 
        
        result = CommandResult.SUCCESS
        if t1=='am' and t2.lower() == 'i':
            player = self.game_state.current_player
            message = "You are on square# "
        elif t1=='is':
            # t2 is a player's initials or name
            message = f'{t2} is on square# '
            player = self.get_player(t2)
        if player is not None:
            current_board_location = player.board_location
            game_square = self.get_player_game_square(player)
            message += str(game_square.number)
            if game_square.square_class == 'Occupation':
                message += " of " + current_board_location.occupation_name + ": '" +  game_square.text + "' " 
            else:    # a border square
                message += ": " + game_square.name
            if game_square.action_text is not None:
                message += "\n" + game_square.action_text
        else:
            message = f'No such player: {t2}'
            result = CommandResult.ERROR
        
        return CommandResult(result, message, False)
    
    def retire(self) -> CommandResult:
        """Retire this player to the retirement corner square (Spring Break, Holiday)
        
        """
        result = CommandResult(CommandResult.SUCCESS, "'retire' command not yet implemented", False)
        return result
    
    def bump(self, who) -> CommandResult:
        """The current player bumps another player occupying the same board square to Unemployment
            Note that it is possible to land on a square occupied by more than one player,
            for example if a player chooses NOT to bump that square will have 2 players.
            In any case the initials of the player to be bumped must be provided.
            Only a single player may be bumped even if there are more than one on the square.
        
        """
        player = self.game_state.current_player
        bumped_player = None
        for p in player.can_bump:
            if p.player_initials == who:
                bumped_player = p
        
        if bumped_player is None:
            result = CommandResult(CommandResult.ERROR, f'Player {who} cannot be Bumped')
        else:
            #
            # find the Unemployment square and place the bumped_player there
            # and also set the is_unemployed flag
            #
            border_square = self._careersGame.find_border_square("Unemployment")
            result = border_square.execute(bumped_player)
        return result
    
    def bankrupt(self) -> CommandResult:
        """The current player declares bankruptcy.
            A bankrupt player looses all cash, experience and opportunity cards and essentially
            restarts the game with configured starting cash and salary, and positioned at the "Payday" square (border square 0).
            The player does retain occupation experience however including any and all college degrees.
        
        """
        result = CommandResult(CommandResult.SUCCESS, "'bankrupt' command not yet implemented", False)
        return result
    
    def pay(self, amount_str, initials=None) -> CommandResult:
        """The current player, or the player whose initials are provided, makes a payment associated with their current board position.
            If the paying player has sufficient cash to make the payment that amount is subtracted
            from their cash on hand and CommandResult.SUCCESS with done_flag = True is returned 
            Otherwise, CommandResult.ERROR is returned with done_flag = False.
            This does NOT bankrupt the player automatically because a player may bargain with other
            player(s) to get a loan to pay off the debt.
            If no such arrangement is made (in the UI), a bankrupt command is sent.
            Experience and Opportunity cards can be transfered from one player to another using the transfer() command.
            
            NOTE - "loans" are not paid off automatically. HOWEVER a player's net worth, which determines total_points,
            will subtract all loan amounts from cash on hand.
            
        """
        amount = int(amount_str)
        player = self.game_state.current_player if initials is None else self.get_player(initials)
        if player.cash >= amount:
            player.cash = player.cash - amount
            message = f'{player.player_initials} paid {amount}'
            return CommandResult(CommandResult.SUCCESS, message, True)
        else:
            message = f'{player.player_initials} has insufficient funds to cover {amount} and must either borrow cash from another player or declare bankruptcy'
            return CommandResult(CommandResult.ERROR, message, False)
        
    def transfer(self, quantity:int, what:str, from_player_number:int) -> CommandResult:
        """Transfers cash, opportunities or experience cards from one player to the current player
            Arguments:
                from_player_number - the player number transferring
                what - "cash", "opportunity", "experience"
                quantity - the amount of cash or number of experience/opportunity cards being transferred
        """
        CommandResult(CommandResult.SUCCESS, "transfer command not implemented", True)
        
    
    def list(self, what='all') ->CommandResult:
        """List the Experience or Opportunity cards held by the current player
            Arguments: what - 'experience', 'opportunity', or 'all'
            Returns: CommandResult.message is the stringified list of str(card).
                For Opportunity cards this is the text property.
                For Experience cards this is the number of spaces (if type is fixed), otherwise the type.
            
        """
        player = self.game_state.current_player
        return GameEngineCommands.list(player, what)    

    def saved(self) -> CommandResult:
        """List the games saved by this master_id, if any
        
        """
        result = CommandResult(CommandResult.SUCCESS, "'saved' command not yet implemented", False)
        return result    

    def load(self, gameid:str) -> CommandResult:
        """Load a previously saved game, identified by the game Id
        
        """
        result = CommandResult(CommandResult.SUCCESS, "'load' command not yet implemented", False)
        return result    

    def who(self, t1:str="am", t2:str="I") -> CommandResult:
        """Who am I or who is <player>
            Returns: A CommandResult where message is the player's info: name, initials, number, SSN (kidding)
                If there is no player with initials t2, return_code is ERROR.
        """
        result = CommandResult.SUCCESS
        if t1=='am' and t2.lower() == 'i':
            player = self.game_state.current_player
            message = player.info()
        elif t1=='is':
            # t2 is a player's initials or name
            player = self.get_player(t2)
            if player is not None:
                message = player.info()
            else:
                message = f'No such player: {t2} '
                result = CommandResult.ERROR
            
        return CommandResult(result, message, True)
    
    def add(self, what, name, initials=None, stars=0, hearts=0, cash=0) -> CommandResult:
        """Add a new player to the Game OR add a degree to the current player or the player whose initials are provided.
    
        """
        if what == 'player':
            sf = SuccessFormula(stars=stars, hearts=hearts, cash=cash)
            player = Player(name=name, initials=initials)
            player.success_formula = sf
            player.salary = self._careersGame.game_parameters['starting_salary']
            player.cash = self._careersGame.game_parameters['starting_cash']
            self._careersGame.add_player(player)        # adds to GameState
            
            message = f'Player "{name}" "{initials} number: {player.number}" added'
        else:    
            # adds a degree in the current (or named) player's degree programs
            # name is the name of the degree program
            player = self.game_state.current_player if initials is None else self.get_player(initials)
            result = self.add_degree(player, name)
            message = result.message
        
        self.log(message)
        return CommandResult(CommandResult.SUCCESS, message, False)
    
    def game_status(self) -> CommandResult:
        """Get information about the current game in progress and return in JSON format
        """
        message =  self.game_state.to_JSON()
        
        return CommandResult(CommandResult.SUCCESS, message, True)
    
    def create(self, edition, master_id, game_type, points, game_id=None) -> CommandResult:
        """Create a new CareersGame.
        
        """
        assert master_id is not None and len(master_id) >= 5
        self._edition = edition    # 'Hi-Tech'
        self._master_id = master_id
        #
        # Create the CareersGame instance and the GameEngineCommands
        #
        self._careersGame = CareersGame(self._edition, master_id, points, game_id, game_type=game_type)
        
        self._game_state = self._careersGame.game_state
        self._gameId = self._careersGame.gameId
        self._logfile_filename = "careers_" + self._careersGame.edition_name
        self._logfile_folder = "/data/log"    # TODO put in Environment
        self._gamefile_folder = "/data/games"
        self._logfile_path = self._logfile_folder + "/" + self._logfile_filename + "_" + self._gameId + ".log"
        self._game_filename_base = f'{self._gamefile_folder}/{self.master_id}_{self.gameId}_game'
        
        self.fp = open(self._logfile_path, "w")   # log file open channel
        self._gameEngineCommands = GameEngineCommands(self._careersGame, self.fp)
        self._gameEngineCommands.trace = self.trace

        message = f'Created game {self._gameId} for {self._master_id}'
        self.log(message)
        return CommandResult(CommandResult.SUCCESS, message, True)
    
    def start(self) -> CommandResult:
        return self._start()
    
    def buy(self, what, qty_str, amount_str) -> CommandResult:
        """Buy a number of items for the current player
            Arguments:
                what - "hearts" | "stars" | "experience" | "opportunity"
                qty - how many to buy (adds to the player's score or card deck)
                amount - cash amount cost
            Returns:
                CommandResult.SUCCESS if the player can cover the cost, otherwise CommandResult.ERROR with an appropriate error message
            Okay to have a negative quantity and zero amount. For example, to lose 1 heart send: "buy hearts -1 0"
        """
        return self._buy(what, qty_str, amount_str)
    
    #####################################
    #
    # Game engine action implementations
    #
    #####################################
        
    def _start(self) -> CommandResult:
        message = f'Starting game {self.gameId}'

        self.log(message)
        self.game_state.set_next_player()    # sets the player number to 0 and the curent_player Player reference
        return CommandResult(CommandResult.SUCCESS, message, True)
    
    def _buy(self, what, qty_str, amount_str) -> CommandResult:
        """Implements the buy command
        """
        player = self.game_state.current_player
        amount = int(amount_str)
        qty = int(qty_str)
        if player.cash < amount:
            return CommandResult(CommandResult.ERROR, f'Insufficient funds {player.cash} for amount {amount}', True)
        player.add_cash(amount)
        if what.lower().startswith('heart'):
            player.add_hearts(qty)
        elif what.lower().startswith('star'):
            player.add_stars(qty)
        elif what.lower().startswith('exp'):
            self.add_experience_cards(player, qty)
        elif what.lower().startswith('opp'):
            self.add_opportunity_cards(player, qty)
        else:
            return CommandResult(CommandResult.ERROR, f'Cannot add {qty} {what}', False)
        return CommandResult(CommandResult.SUCCESS, f'{qty} {what} added', True)

    def can_enter(self, occupation_name, player:Player):
        """Determine if this player can enter the named Occupation
            This checks if the player meets the entry conditions, namely:
                * it's college and they have the tuition amount in cash
                * they've previously completed this occupation and can therefore enter for free
                * or they have a qualifying degree and can therefore enter for free
                * or they have executed an "All expenses paid" Opportunity card
                * or they have sufficient cash to cover the entry fee 
        """

        occupation = self._careersGame.occupations[occupation_name]   # Occupation instance
        entry_fee = occupation.entryFee
        has_fee = player.cash >= entry_fee
        occupationClass = occupation.occupationClass
        # anyone can go to college if they have the funds
        if occupationClass == 'college' and has_fee:
            return True    
        
        #
        # check occupation record for prior trips through 
        #
        if occupation_name in player.occupation_record and player.occupation_record[occupation_name] > 0:
            return True
        #
        # check degree requirements
        #
        degreeRequirements = occupation.degreeRequirements
        degreeName = degreeRequirements['degreeName']
        numberRequired = degreeRequirements['numberRequired']
        if degreeName in player.my_degrees and player.my_degrees[degreeName] >= numberRequired:
            return True
        #
        # is the player using a  "All expenses paid" Opportunity card ?
        #
        if player.opportunity_card is not None:
            if player.opportunity_card.expenses_paid:
                return True
        
        return has_fee

    
    def _execute_opportunity_card(self,  player:Player, opportunityCard:OpportunityCard=None) -> CommandResult:
            player.opportunity_card = opportunityCard
            message = f'{player.player_initials} Playing: {opportunityCard.text}'
            #
            # Now execute this Opportunity card
            #
            self.log(message)
            result = CommandResult(CommandResult.SUCCESS, message, False)   #  TODO
            return result                   
    
    def _execute_experience_card(self,  player:Player, experienceCard:ExperienceCard, spaces=0) -> CommandResult:
            player.experience_card = experienceCard
            nspaces = experienceCard.spaces
            if experienceCard.spaces == 0 and experienceCard.type != 'fixed':    # must be a wild card
                nspaces = spaces

            message = f'{player.player_initials} Moving: {nspaces} spaces'
            self.log(message)
            result = CommandResult(CommandResult.SUCCESS, message, False)   #  TODO
            return result        
    
    def execute_game_square(self, player:Player, board_location:BoardLocation) -> CommandResult:
        """Executes the actions associated with a given BoardLocation and Player
        
        """
        game_square = self.get_player_game_square(player)
        if board_location.occupation_name is not None:
            result = self._execute_occupation_square(player, game_square, board_location)
        else:
            result = self._execute_border_square(player, game_square, board_location)
        
        return result
        
    def _execute_occupation_square(self, player:Player, game_square:OccupationSquare, board_location:BoardLocation) -> CommandResult:
        message = f'execute_occupation_square {board_location.occupation_name}  {board_location.occupation_square_number} for {player.player_initials}'
        self.log(message)
        
        return CommandResult(CommandResult.SUCCESS, message, False)
    
    def _execute_border_square(self, player:Player, game_square:BorderSquare, board_location:BoardLocation) -> CommandResult:
        message = f'{player.player_initials} landed on {game_square.name}  ({board_location.border_square_number})'
        self.log(message)
        result = game_square.execute(player)
        result.message = message + "\n" + result.message
        #
        # if there is a next action to perform then do it
        #
        if result.next_action is not None:
            action_result = self.execute_command(result.next_action, player)
            result.message = result.message + "\n" + action_result.message
            result.return_code = action_result.return_code
            result.done_flag = action_result.done_flag
        return result
    
    def _get_next_square_number(self, player:Player, num_spaces:int) -> int:
        """Gets the next square number given the number of spaces to advance.
            Arguments:
                player - the Player
                num_spaces - the number of spaces to advance. Must be >0 to go anywhere, but this doesn't check.
            Returns: the next square number, depending on whether the player is currently on a BorderSquare or OccupationSquare
            NOTE that the square number returned could be out of bounds for the occupation or along the border.
            This is handled by goto() which does the actual placement.
        """
        board_location = player.board_location
        game_square = self.get_player_game_square(player)       # could be BorderSquare or OccupationSquare

        #
        # advance that number of spaces if permitted to do so. 
        # If the player is on the occupation entrance square, the occupation_square_number will be -1
        # Squares are numbered starting with 0
        # 
        if game_square.square_class == 'occupation':
            next_square_number = board_location.occupation_square_number + num_spaces    # could be > size of the occupation, that's handled by goto()
        else:
            next_square_number = board_location.border_square_number + num_spaces        # could be > size of the board, that's also handled by goto()
            
        return next_square_number
    

    def _goto(self, square_number:int, player:Player) -> CommandResult:
        """Immediately place the designated player on the designated BorderSquare OR OccupationSquare and execute that square.
            If the current player is in an occupation, this places the player on square_number of that Occupation.
            Otherwise, the square_number refers to a BorderSquare.
            NOTE that the border square number could be out of range. i.e. > game size. 
            If so, the square number adjusted and then the pass_payday() action is executed.
            
            NOTE that when in an Occupation the designated square_number could be out of range. i.e. > the occupation exit_square_number.
            If so, the player is advanced to the next BorderSquare and the exit occupation logic is executed.
            
        """
        game_square = self.get_player_game_square(player)   # where player currently is on the board
        board_location = player.board_location
        result = None
        if game_square.square_class == 'occupation':        # If player is currently in or completing an Occupation
            
            occupation_name =  player.board_location.occupation_name
            occupation = self._careersGame.occupations[occupation_name]
            if square_number >= occupation.size:
                
                exit_result =  self.exit_occupation(player, board_location)
                
                #
                # go to next border square and update board_location after the occupation exit
                #
                board_location.border_square_number = square_number - occupation.size + occupation.exit_square_number - 1
                board_location.occupation_name = None
                game_square =  self._careersGame.get_border_square(board_location.border_square_number)
                board_location.border_square_name = game_square.name                
                
                result = self.execute_game_square(player, board_location)
                result.message = exit_result.message + "\n" + result.message
                #return result
            else:    # next square is in this occupation
                board_location.occupation_square_number = square_number
                return self.execute_game_square(player, board_location)
                
        else:   # goto designated border square
            if square_number >= 0 and \
               square_number < self._careersGame.game_board.game_layout_dimensions['size'] and \
               square_number > board_location.border_square_number :
                player = self.game_state.current_player
                border_square = self._careersGame.get_border_square(square_number)
                board_location.border_square_number = square_number
                board_location.border_square_name = border_square.name
                board_location.occupation_name = None
                #
                # execute this game square
                # unless it's a travel_square and we just game from a travel_square
                # otherwise we'd get into an endless travel loop
                #
                if border_square.square_type == 'travel_square' and self.was_prior_travel(player):
                    result = CommandResult(CommandResult.SUCCESS, "", True)
                else:
                    result = self.execute_game_square(player, board_location)
                #return result
            else:    # player passed or landed on Payday
                if square_number >  board_location.border_square_number :
                    square_number = square_number - self._careersGame.game_board.game_board_size
                border_square = self._careersGame.get_border_square(square_number)
                board_location.border_square_number = square_number
                board_location.border_square_name = border_square.name
                payday_result = self.pass_payday(player)
                #
                # again, check travel arrangements
                #
                if border_square.square_type == 'travel_square' and self.was_prior_travel(player):
                    result = CommandResult(CommandResult.SUCCESS, "", True)
                else:
                    result = self.execute_game_square(player, board_location)
            
                result.message = payday_result.message + "\n" + result.message
                #return result
        #
        # if another player is on that square AND the square is NOT Unemployment, they can be bumped
        #
        other_players = self.who_occupies_my_square(player)
        if player.current_border_square_name() != "Unemployment":
            if len(other_players) > 0:
                initials = [p.player_initials for p in other_players]
                result.message = result.message + f'\n{player.player_initials} can bump {initials}'
        player.can_bump = other_players   # could be an empty list
        return result

    def exit_occupation(self, player, board_location:BoardLocation) -> CommandResult:
        """Applies exiting an occupation rules when a player exits an occupation path.
            Exiting can be done by rolling out, using an Experience, or using an Opportunity to go somewhere else.
            The occupation could be College ("occupationClass" : "college") or a regular Occupation ("occupationClass" : "occupation")
            * if the player entered the Occupation via Opportunity card, that card is removed from the player's hand
            * if the player completed the Occupation, credit is applied to the player's occupation record and up to 3 Experience cards given
            
            Note that exit_occupation does NOT update the player's board position.  
            That is done by goto() which calls this method before updating the board position.
            So upon entry, border square location is the occupation entrance square for this occupation (or college).
            Note also that the player's salary is NOT adjusted when completing college. That is done by the add_degree() method.
            
        """
        nexperience = 0
        trips = 1
        if board_location.occupation_name in player.occupation_record:
            trips = player.occupation_record[board_location.occupation_name]   # number of trips not counting this one
            player.occupation_record[board_location.occupation_name] = trips + 1
            
        else:
            player.occupation_record[board_location.occupation_name] = trips
        
        #
        # No experience given for completing College
        # 
        game_square = self._careersGame.get_border_square(board_location.border_square_number)
        if game_square.square_class == 'occupation_entrance_square':
            if trips <= 3:  # at most 3 experience cards can be given
                nexperience = trips
            else:
                nexperience = 3

        self.add_experience_cards(player, nexperience)
        
        message = f'{player.initials} Leaving {board_location.occupation_name}, collects {nexperience} Experience cards'
        self.log(message)
        result = CommandResult(CommandResult.SUCCESS, message, True)
        return result
    
    def add_experience_cards(self, player:Player, ncards:int):
        deck = self._careersGame.experience_cards     # ExperienceCardDeck
        for i in range(ncards):
            card = deck.draw()
            player.add_experience_card(card)
            
    def add_opportunity_cards(self, player:Player, ncards:int):
        deck = self._careersGame.opportunities        # OpportunityCardDeck
        for i in range(ncards):
            card = deck.draw()
            player.add_opportunity_card(card)
        
    def pass_payday(self, player:Player) -> CommandResult:
        """Performs any actions associated with landing on or passing the Payday square.
            Count laps (which may or may not be used) and dole out appropriate salary.
            Arguments:
                player - current Player reference
            The player's board location reflects the new position which will have a border_square_number >= 0.
        """
        game_square = self._careersGame.get_border_square(0)    # Payday is always square 0
        result = game_square.execute(player)
        self.log(result.message)
        return result
    
    def was_prior_travel(self, player) -> bool:
        """Returns True if the player's prior border position was a travel square, False otherwise
            This is needed in order to avoid endless travel hops.
        """
        result = False
        ps = player.board_location.prior_border_square_number
        if ps is not None and self._careersGame.game_board.border_squares[ps].square_type == 'travel_square':
            result = True
        return result
        
    def add_degree(self, player, degreeProgram) -> CommandResult:
        """Adds a degree to the player and adjusts the salary as needed.
            The maximum number of degrees a player can have in any degree program is "maxDegrees".
            Player's Salary is not adjusted if their number of degrees exceeds that.
        """
        game_degrees = self._careersGame.college_degrees
        degree_names = game_degrees['degreeNames']
        if degreeProgram not in game_degrees['degreePrograms']:
            return CommandResult(CommandResult.ERROR, f"No such degree program: {degreeProgram}", False)
        
        max_allowed = game_degrees['maxDegrees']
        salary_increases = game_degrees['salaryIncreases']
        my_degrees = player.my_degrees
        ndegrees = 0
        salary_inc = 0
        if degreeProgram in my_degrees:
            ndegrees = player.my_degrees[degreeProgram]
        
        if ndegrees == 0:
            player.my_degrees[degreeProgram] = 1
            salary_inc = salary_increases[0]
            player.salary = player.salary + salary_inc   # automatically adds to salary_history
            
        elif ndegrees + 1 <= max_allowed:
            salary_inc = salary_increases[ndegrees]
            player.my_degrees[degreeProgram] = ndegrees + 1
            player.salary = player.salary + salary_inc
        
        else:
            ndegrees = 3  # already maxed out
        
        message = f'{player.player_initials} awarded {degree_names[ndegrees]} degree in {degreeProgram}'
        if salary_inc > 0:
            currency = self._careersGame.game_parameters['currency']
            message += f' and a Salary increase of {salary_inc} {currency}'
        
        return CommandResult(CommandResult.SUCCESS, message, True)
        
    def who_occupies_my_square(self, player) -> List[Player]:
        """If the game square currently occupied by player is also occupied by another player(s), return those players.
            The player landing on an occupied square may bump that player to Unemployment.
            Arguments: 
                player - the Player landing on the designated square
            Returns: a list of Player on the square occupied by player, or an empty list if none.
        """
        plist = []
        occupation_name = player.current_occupation_name()      # could be None
        for ap in self._game_state.players:
            if player.number == ap.number:
                continue    # it's me!
            if occupation_name is None:     # player is on a border square
                if player.current_border_square_number() == ap.current_border_square_number():
                    plist.append(ap)
            else:   # player is in an occupation
                if ap.current_occupation_name() == occupation_name and ap.current_occupation_square_number() == ap.current_occupation_square_number():
                    plist.append(ap)
                
        return plist
    
        