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
from game.opportunityCard import OpportunityCard, OpportunityType, OpportunityActionType
from game.experienceCard import ExperienceCard, ExperienceType
from game.boardLocation import BoardLocation
from game.successFormula import SuccessFormula
from game.borderSquare import BorderSquare, BorderSquareType
from game.occupationSquare import OccupationSquare
from game.gameSquare import GameSquare, GameSquareClass
from game.gameEngineCommands import GameEngineCommands
from game.environment import Environment
from game.gameState import GameState
from game.gameConstants import PendingActionType, SpecialProcessingType, GameType, GameParametersType, PlayerType
from game.turnHistory import TurnHistory
from game.logger import Logger

from datetime import datetime
import random
from typing import List
import os, logging
from threading import Lock

class CareersGameEngine(object):
    """CareersGameEngine executes the action(s) associated with each player's turn.
    Valid commands + arguments:
        command :: <roll> | <use> | <use insurance> | <update> | <retire> | <bump> | <bankrupt> | 
                   <list> | <status> | <info> | <quit> | <done> | <end game> |
                   <saved games> | <save> | <load> | <query> | <enter> | <goto> | <add> | <add degree> |
                   <pay> | <transfer> | <game_status> | <create> | <start> | <buy> | <perform> | <log> | <turn_history>
                   
        <use> :: "use"  <what> <card_number>
            <what> :: "opportunity" | "experience" | "roll"
            <card_number> :: <integer> | '[' <integer list> ']'
        <use insurance> :: "use_insurance"
        <update>  :: "update" <playerID> <success_formula>   ;update a player's success formula
            <success_formula>  :: nstars nhearts cash
        <roll> :: "roll"  [1|2]                 ;roll 1 or 2 dice depending on where the player is on the board
        <retire> :: "retire"                    ;immediate go to retirement square (Spring Break, Holiday)
        <bump> :: "bump" player_initials        ;bump another player, who must be on the same square as the bumper
        <bankrupt> :: "bankrupt"                ;declare bankruptcy
        <list> :: "list"  ["occupations" | "commands" | "all" | <card_type> ]  ;list occupations completed, command history
            <card_type> :: "opportunity" | "experience"                        ;or my opportunities or experience cards
        <status> :: "status"                    ;display a player's cash, #hearts, #stars, salary, total points, and success formula, pending and loan info
        <info> :: "info"                        ;returns JSON-formatted player info
        <quit> :: "quit" player_initials        ;current player leaves the game, must include initials
        <done> :: "done" | "next"               ;done with my turn - next player's turn
        <end game> :: "end game"                ;saves the current game state then ends the game
        <saved games> :: "saved games"          ;list any saved games by date/time and game_id
        <save> :: "save" <how>                  ;saves the current game state to a file in the specified format
            <how> ::  "json" | "pkl"
        <load> :: "load" game-id                ;load a game and start play with the next player
        <query> :: "where" <who>                ;gets info on a player's current location on the board
            <who> :: "am I" | "is" <playerID>
        <playerID> :: player_name | player_initials
        <enter> :: "enter" <occupation_name> [<square_number>]                 ;enter occupation at occupation square square_number
        <goto> :: "goto" <square_number> | <square_name>                       ;go to border square square_number
        <add> :: "add player" player_name player_initials cash stars hearts    ;adds a new player to the game

        <add degree> :: "add degree" <degree program>
            <degree program> :: See collegeDegrees-<edition name>.json "degreePrograms"
        <pay> :: "pay" amount                ;current player makes a payment associated with their current board location
        <transfer> :: "transfer" quantity ("cash" | "opportunity" | "experience) player_number
        <game_status> :: "game_status"
        <create> :: "create" <edition> <game_type> points  [id]      ;create a new CareersGame with specified total points or total time (in minutes) and optional game_id
            <edition> :: "Hi-Tech" | "UK   ;supports multiple editions
            <game_type> ::  'points' | 'timed'
        <start> :: "start"                    ;starts a newly created CareersGame
        <buy>  :: "buy"  ( "hearts" | "stars" | "experience" | "insurance" | "opportunity" ) quantity cash_amount  ;buy some number of items for the cash_amount provided
        <perform> :: "perform roll <ndice>"      ; roll the dice and return the result without moving
            <ndice> :: 0 | 1 | 2
        <resolve_pending> :: "resolve" choice [pending_amount]    ; resolve a pending action and amount. choice is the player's choice based on the game_square's "pending_action",
            <choice> :: * | <pending_action>                      ; * = the most recently added pending_action, else the pending_action to resolve such as "buy_hearts"
        <log> :: "log_message" <text>    ; writes <text> to the log file
        <advance> :: "advance" <nspaces>     ; advance a given number of spaces from current position
        <turn_history> ::  "turn_history"    ; displays the current player's complete TurnHistory in JSON format
        
    """
    _lock = Lock()
        
    def __init__(self, careers_game:CareersGame=None, game_id:str=None, loglevel='warning', installationId="", edition=""):
        '''
        Constructor
        '''
        self._careersGame = careers_game    # create a new CareersGame with create()
        self._debug = False                 # traces the action by describing each step and logs to a file
        self._start_date_time = datetime.now()
        self._installationId = installationId      # provided by the UI or the GameRunner
        self._current_player = None
        self._admin_player = Player(number=-1, name='Administrator', initials='admin')
        self._gameEngineCommands = None     # no CareersGame yet
        self.currency_symbol = None         # value set with create()
        self._game_state = None             # set with create()
        self._game_id = self._create_game_id(installationId) if game_id is None else game_id
            
        self._init_logging(loglevel, self._game_id, edition)
    
    def _init_logging(self, loglevel:str, game_id, edition):
        
        log_levels = {"debug":logging.DEBUG, "info":logging.INFO, "warning":logging.WARNING, "error":logging.ERROR, "critical":logging.CRITICAL}
        level = log_levels[loglevel]
        self._debug = (loglevel=='debug')
        
        self._logfile_filename = f'{game_id}_{edition}'
        
        self._dataRoot = Environment.get_environment().package_base

        self._logfile_folder = os.path.join(self._dataRoot, 'log')
        self._gamefile_folder = os.path.join(self._dataRoot, 'games')
        self._logfile_path = os.path.join(self._logfile_folder, self._logfile_filename + ".log")
        self._game_filename_base = os.path.join(f'{self._gamefile_folder}', f'{self.game_id}_game')
        
        if(not os.path.exists(self._logfile_folder)):
            os.mkdir(self._logfile_folder)
        
        if(not os.path.exists(self._gamefile_folder)):
            os.mkdir(self._gamefile_folder)
        
        # configure the logger
        self._logger = Logger(self.game_id,  edition, self._logfile_path, level=level)
        

    def _create_game_id(self, installation_id) ->str :
        """Create a unique game id (guid) for this game.
            This method acquires a lock to insure uniqueness in a multi-process/web environment.
            Format is based on current date and time and installationId for example ZenAlien2013_20220908-140952-973406-27191
        """
        CareersGameEngine._lock.acquire()
        today = datetime.now()
        gid = installation_id +  '_{0:d}{1:02d}{2:02d}_{3:02d}{4:02d}{5:02d}_{6:06d}_{7:05d}'\
            .format(today.year, today.month, today.day, today.hour, today.minute, today.second, today.microsecond, random.randint(10000,99999))
        CareersGameEngine._lock.release()
        return gid
    
    @property
    def dataRoot(self) ->str:
        return self._dataRoot
    
    @property
    def logfile_name(self):
        return self._logfile_name
    
    @property
    def logfile_path(self):
        return self._logfile_path
    
    @property
    def game_id(self):
        return self._game_id
    
    @game_id.setter
    def game_id(self, value):
        self._game_id = value
    
    @property
    def installationId(self):
        return self._installationId
    
    @property
    def debug(self) -> bool:
        return self._debug
    
    @debug.setter
    def debug(self, value:bool):
        self._debug = value
        
    @property
    def game_state(self) -> GameState:
        return self._game_state
    
    @game_state.setter
    def game_state(self, value:GameState):
        self._game_state = value
    
    @property
    def careersGame(self) -> CareersGame:
        return self._careersGame
    
    @careersGame.setter
    def careersGame(self, value:CareersGame):
        self._careersGame = value
    
    def log_info(self, *message):
        """Write info-level message to the log file and if debug is set, also to the console
            
        """
        txt = " ".join(message)
        if self.debug:
            print(txt)
        logging.info(txt)
            
    def log_message(self, *message) -> CommandResult:
        """The command version of log.
        """
        self.log_info(*message)
        return CommandResult(CommandResult.SUCCESS, "", True)

    def execute_command(self, command:str, aplayer:Player, args:list=[]) -> CommandResult:
        """Executes a command for a given Player.
            This also updates Turn.commands.
            Arguments:
                command - the command name, for example "roll".
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
            logging.debug(f'{player.player_initials}: {command}')
            if command is None or len(command) == 0:
                return CommandResult(CommandResult.SUCCESS, "", False)
            cmd_result = self._evaluate(command, args)
            player.add_command(command)    # adds to player's command history and current Turn
            
            board_location = player.board_location    # current board location AFTER the command is executed
            if command.lower() != "log_message":      # no need to log twice
                logging.debug(f'  {player.player_initials} results: {cmd_result.return_code} {cmd_result.message}\n{board_location}')
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
        logging.debug("_evaluate: " + command)
        try:
            command_result = eval(command)
        except Exception as ex:
            message = f'"{command}" : Invalid command format or syntax\nexception: {str(ex)}'
            command_result = CommandResult(CommandResult.ERROR,  message,  False, exception=ex)
            logging.error(message)
        return command_result
    
    def get_player_game_square(self, player:Player) -> GameSquare:
        game_square = self._careersGame.get_game_square(player.board_location)
        return game_square
    
    def get_player(self, pid:str) -> Player | None :
        """Gets a Player by initials, name, or number
            Arguments:
                pid - string that represents a player number, name or initials
            Returns: Player instance or None if no player with the given ID exists.
            Note that name/initials are NOT case sensitive.
        """
        player = None
        if pid.isdigit():
            player = self.game_state.players[int(pid)]
        else:   # lookup the player by name or initials
            players = self.game_state.players
            lc_pid = pid.lower()
            for p in players:
                if p.player_initials.lower() == lc_pid or p.player_id  == lc_pid:
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
            A specific roll of no spaces can be forced by specifying number_of_dice=0.
            This will cause the player to stay where they are and will execute the current square again.
            roll is implemented by the _advance(...) function.
        """
        player = self.game_state.current_player
        if not player.can_roll:
            return CommandResult(CommandResult.ERROR, "Not your turn to roll!", True)
        
        ndice = number_of_dice
        game_square = self.get_player_game_square(player)       # could be BorderSquare or OccupationSquare

        if self.is_in_occupation(game_square, player):
            ndice = 1
        
        dice = random.choices(population=[i for i in range(1,7)], k=ndice)
        num_spaces = sum(dice)
        logging.info(f' {player.player_initials}  rolled {num_spaces} {dice}')    # INFO
        return self._advance(num_spaces, dice)
            
    
    def advance(self, num_spaces, dice:List[int]|None=None) -> CommandResult:
        """Advance a given number of spaces
            Arguments:
                number_of_spaces - must be >= 0 and < 42
                dice - optional dice roll as List[int], default is None
        
        """
        if self._careersGame.game_parameters_type is GameParametersType.PROD:
            return CommandResult(CommandResult.ERROR, "'advance' command not allowed in production mode", True)
        else:
            return self._advance(num_spaces, dice)
        
    def _advance(self, num_spaces, dice:List[int]|None=None) -> CommandResult:
        assert(num_spaces >= 0 and num_spaces <42)
        player = self.game_state.current_player

        next_square_number = self._get_next_square_number(player, num_spaces)
        message = f' {player.player_initials}  rolled {num_spaces} {dice}, next_square {next_square_number}' if dice is not None \
            else f' {player.player_initials}  advances {num_spaces}, next_square {next_square_number}'
        self.log_info(message)
        print(message)
        #
        # check if player is on a holiday
        # 
        if player.on_holiday:
            game_square = self.get_player_game_square(player)    # HOLIDAY square
            must_roll = game_square.special_processing.must_roll
            if num_spaces in must_roll:    # player may remain
                pending_action = player.pending_actions.get_pending_action(PendingActionType.STAY_OR_MOVE)    # there's a system problem if not found
                pending_action.pending_dice = dice # if they choose to move, could be None
                result = CommandResult(CommandResult.NEED_PLAYER_CHOICE, f'{message} and may remain on {game_square.name}', False)
            else:
                player.clear_pending(PendingActionType.SELECT_DEGREE)       # clear all except SELECT_DEGREE
                result = self.goto(next_square_number)
            
        #
        # check if the player is Unemployed or sick and if so, if the roll allows them to move
        # If dice is None, can_player_move will return True
        else:
            canmove, result = self._gameEngineCommands.can_player_move(player, dice)
            logging.debug(result.message)
            if canmove:
                #
                # clear any pending action - use it or lose it!
                # and place the player on the next_square_number
                #
                player.clear_pending()
                result = self.goto(next_square_number)
                
        return result

    
    def update(self, who:str, nhearts:int, nstars:int, cash_amount:int) -> CommandResult:
        '''Update a player's success formula.
        '''
        player = self.get_player(who)
        if player is None:
            result = CommandResult(CommandResult.ERROR, f'Player {who} does not exist (as far as we know)', True)
        else:
            if (nhearts + nstars + cash_amount) == self.careersGame.game_state.total_points:
                player.success_formula = SuccessFormula(nstars, nhearts, cash_amount)
                result = CommandResult(CommandResult.SUCCESS, f"{who}'s success formula updated to {nstars} stars, {nhearts} hearts, {self.currency_symbol}{1000*cash_amount} money", True)
            else:
                result = CommandResult(CommandResult.ERROR, f'Total points must add up to {self.careersGame.game_state.total_points}', True)
        
        return result
    
    def use(self, what, card_number, spaces:str|int|None=None) -> CommandResult:
        """Use an Experience or Opportunity card in place of rolling the die.
            Experience and Opportunity cards are identified (through the UI) by number, which uniquely
            identifies the card function. i.e. Cards having the same "number" are identical
            with respect to the end result. There are generally more than 1 card of a given number
            in the deck and this is identified by the ordinal "ncard".
            Arguments:
                what - "opportunity", "experience", "roll"
                card_number - the unique number for this card. Corresponds to card.number OR
                    if what == 'roll', the dice roll as a list. For example, "[3, 4]"
                spaces - required for Experience wild cards, the number of spaces to move. Can be + or
                         For card types choose_destination, choose_occupation spaces can be the chosen destination.
                         This is optional but if specified it resolves the choice (so sending a "resolve" command is not needed).
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
                leave_unemployment = thecard.opportunity_type is OpportunityType.ACTION and thecard.action_type is OpportunityActionType.LEAVE_UNEMPLOYMENT
                if leave_unemployment and not player.is_unemployed:
                    result = CommandResult(CommandResult.ERROR, f"You need to be Unemployed to use {thecard.opportunity_type.value} ", False)
                    return result
                
                if player.is_unemployed:    # player is sitting in Unemployment
                    if leave_unemployment:
                        player.opportunity_card = thecard
                        player.can_use_opportunity = True
                        result = self._execute_opportunity_card(player, opportunityCard=thecard, spaces=spaces)
                    else:
                        result = CommandResult(CommandResult.ERROR, f"use can't use a '{thecard.opportunity_type.value}' here ", False)
                    return result
                
                player.opportunity_card = thecard
                #
                # cannot use 2 Opportunities in the same turn except if
                # the first is extra_turn, leave_unemployment
                #
                if thecard.opportunity_type is OpportunityType.ACTION and \
                 ( thecard.action_type is OpportunityActionType.LEAVE_UNEMPLOYMENT or thecard.action_type is OpportunityActionType.EXTRA_TURN):
                    player.can_use_opportunity = True
                else:
                    player.can_use_opportunity = False
                
                result = self._execute_opportunity_card(player, opportunityCard=thecard, spaces=spaces)
                
        elif what.lower() == 'experience' and player.can_roll:    # Can I use an Experience card?
            cards = player.get_experience_cards()   # dict with number as the key
            thecard_dict = cards.get(card_number, None)
            if thecard_dict is None:    # no such card
                result = CommandResult(CommandResult.ERROR, f"No {what} card exists with number {card_number} ", False)
            else:
                thecard = thecard_dict['card']
                player.experience_card = thecard
                result = self._execute_experience_card(player, experienceCard=thecard, spaces=spaces)
                
        elif what.lower() == "roll":        # use a pre-existing dice roll.
            # card_number is a string having the dice roll
            logging.debug(f'use roll {card_number}')
            diestr = card_number.lstrip(' [').rstrip('] ').split(",")
            die = [int(s) for s in diestr]
            result = self.roll(player, die)
            
        elif what.lower() == "insurance":
            result = self.use_insurance()
            
        else:
            result = CommandResult(CommandResult.ERROR, f"use can't use a '{what}' here ", False)
            
        return result
    
    def use_insurance(self) -> CommandResult:
        """Use insurance, if you have it, to avoid paying a penalty or loosing hearts/stars/salary
            Returns: CommandMessage with return_code == SUCCESSFUL if okay, == ERROR if no insurance
                or not applicable in this case.
            A player uses insurance immediately after the loss. This will restore the amounts
            or quantities lost. For example, say a player pays 4000 after landing on DivorceCourt.
            After playing use_insurance that amount is restored. Hearts and Stars restored in the same way.
            
        """
        player = self.game_state.current_player
        if player.is_insured:
            message = ""
            if player.point_losses["cash"] > 0:
                amount = player.point_losses["cash"]
                player.add_cash(amount)
                message += f"cash amount {amount} restored\n"
            if player.point_losses["hearts"] > 0:
                amount = player.point_losses["hearts"]
                player.add_hearts(amount)
                message += f"{amount} happiness points restored\n"
            if player.point_losses["stars"] > 0:
                amount = player.point_losses["stars"]
                player.add_stars(amount)
                message += f"{amount} fame points restored\n"
            if player.point_losses["salary"] > 0:
                amount = player.point_losses["salary"]
                player.add_to_salary(amount)
                message += f"{player.salary} salary restored"
            player.clear_point_losses()
            player.is_insured = False    # lose insurance but can buy again immediately after use
            game_square = self._careersGame.find_border_square("BuyInsurance")
            player.add_pending_action(PendingActionType.BUY_INSURANCE, game_square_name=game_square.name, amount=game_square.special_processing.get_amount())
            result = CommandResult(CommandResult.SUCCESS, message, False)
        else:
            result = CommandResult(CommandResult.ERROR, "You don't have insurance!", False)
        return result
    
    def _enter(self, occupation_name:str) -> CommandResult:
        return self.enter(occupation_name, internal_use=True)
        
    def enter(self, occupation_name:str, internal_use=False) -> CommandResult:
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
            In production mode, the player must be on the occupation's entry square.
        """
        player = self.game_state.current_player
        if occupation_name in self._careersGame.occupation_names:
            occupation = self._careersGame.occupations[occupation_name]   # Occupation instance
            occupation_entrance_square = self._careersGame.get_occupation_entrance_squares()[occupation_name]    # BorderSquare instance
            current_board_location = player.board_location
            message = None
            entry_ok = True
            meets_criteria = False
            #
            # if player used an Opportunity to get here, remove that from their deck and set their opportunity_card to None
            # also the player can immediately roll in to the Occupation
            #
            if player.opportunity_card is not None and player.opportunity_card.opportunity_type is OpportunityType.OCCUPATION and player.opportunity_card == occupation_name:
                player.used_opportunity()
            else:
                if not internal_use and \
                 (self._careersGame.game_parameters_type is GameParametersType.PROD and current_board_location.border_square_name != occupation_entrance_square.name):
                    entry_ok = False
                    message = "You must be on the Occupation entry square to use 'enter'"
                else:
                    meets_criteria, entry_fee, message = self._gameEngineCommands.can_enter(occupation, player)        # this also checks the Opportunity card used (if any)

            if entry_ok and meets_criteria:
                #
                # in production mode a player must either be on the occupation's entry square
                # or have used an Opportunity to get there
                #
                
                player.cash = player.cash - entry_fee
                player.board_location.border_square_number = occupation_entrance_square.number
                player.board_location.border_square_name=occupation_entrance_square.name
                player.board_location.occupation_name=occupation_name
                player.board_location.occupation_square_number = -1     # still need to roll or use a card

                result = self.where("am","I")
                return CommandResult(result.return_code, f'{result.message}', True)
            else:
                return CommandResult(CommandResult.ERROR, message, False)
        else:
            return CommandResult(CommandResult.ERROR, "No such occupation", False)
    
    def status(self, initials:str=None) -> CommandResult:
        player = self.game_state.current_player if initials is None else self.get_player(initials)
        if self.game_state.game_type is GameType.TIMED:
            player.time_remaining = self.game_state.get_time_remaining()
        message = player.player_info(include_successFormula=True, outputFormat='text')
        result = CommandResult(CommandResult.SUCCESS,  message, True)
        return result
    
    def info(self, initials:str=None) -> CommandResult:
        """Gets player info in JSON format.
            Arguments:
                initials - optional player player_initials, default if not specified is the current player
            Returns:
                CommandResult where the message is JSON-formatted player_info (same information returned by 'status') 
        """
        player = self.game_state.current_player if initials is None else self.get_player(initials)
        if self.game_state.game_type is GameType.TIMED:
            player.time_remaining = self.game_state.get_time_remaining()
        include_success_formula = self.game_state.game_type is GameType.POINTS
        message = player.player_info(include_successFormula=include_success_formula, outputFormat='json')
        result = CommandResult(CommandResult.SUCCESS,  message, True)
        return result
    
    def turn_history(self, initials:str=None) ->CommandResult:
        """turn_history command
        """
        player:Player = self.game_state.current_player if initials is None else self.get_player(initials)
        message = player.turn_history.to_JSON()
        result = CommandResult(CommandResult.SUCCESS,  message, True)
        return result       
    
    def done(self) -> CommandResult:
        """End my turn, update turn history, and go to the next player
        """
        current_player = self.game_state.current_player
        ###################################################################################
        # is there a pending action for this player? This might include a pending penalty.
        # clear any point losses for this turn
        ###################################################################################
        self._resolve_pending(current_player)
        current_player.clear_point_losses()
        #
        # Update the AFTER of this turn; create a new Turn and calculate the outcome
        #
        turn_history = current_player.turn_history
        next_turn_number = turn_history.next_turn_number()
        player_info = current_player.player_info(include_successFormula=True, outputFormat="dict", include_degrees=True, include_card_values=True)
        turn_number = self.game_state.turn_number
        current_player.turn_history.add_player_info(turn_number, TurnHistory.AFTER_KEY, player_info)
        theTurn = current_player.turn_history.create_turn(turn_number)
        self.log_info(f"turn: {turn_number} outcome: {theTurn.outcome}\n")
        
        # The AFTER of this turn is now the BEFORE of the player's next turn
        current_player.turn_history.turn_number = next_turn_number
        current_player.turn_history.add_player_info(next_turn_number, TurnHistory.BEFORE_KEY, player_info)
        
        
        #
        # has this player won the game?
        #
        if self.game_state.is_game_complete():    # somebody won!
            winning_player = self.game_state.winning_player
            save_result = self.save()
            game_time = self.game_state.get_elapsed_time()
            message = f'The game is over, the winner is {winning_player.player_initials} with {winning_player.total_points()} points. '
            message += f'Game time: {game_time} minutes'
            message += f'\nGame saved as: {save_result.message}'
            result = CommandResult(CommandResult.TERMINATE, message, True)
            return result
    
        current_player.board_location.reset_prior()            # this player's prior board position no longer relevant
        #
        # SELECT_DEGREE can carry over - remove all the others
        #
        # cp.clear_pending(PendingActionType.SELECT_DEGREE)
        
        npn = self.game_state.set_next_player()    # sets current_player and returns the next player number (npn) and increments turns
        player = self.game_state.current_player
        #player.opportunity_card = None
        player.experience_card = None
        player.can_use_opportunity = True
        if current_player.number != player.number:    # could be only 1 player if doing a solo game
            current_player.can_roll = False
        #
        # save the Game on change of turns
        #
        self._gameEngineCommands.save_game(self._game_filename_base, self.game_id, how='pkl')
        result = CommandResult(CommandResult.SUCCESS,  f"{current_player.player_initials} Turn is complete, {player.player_initials}'s ({npn}) turn " , True)
        return result
    
    def next(self) -> CommandResult:
        """Synonym for done - go to the next player
        """
        return self.done()
    
    def end(self, save:str=None) -> CommandResult:
        """Ends the game, saves the current state if specified, and exits.
        """
        self.log_info("Ending game: " + self.game_id)
        self._careersGame.end_game()
        if save is not None and save.lower()=='save':    # save the game state first
            sg_result = self.save()
            result = CommandResult(CommandResult.TERMINATE, f'Game is complete and saved to file: {sg_result.message}', True)
        else:
            result = CommandResult(CommandResult.TERMINATE, "Game is complete" , True)
            
        #
        # Update each player's turn history and add the final after_info
        #
        for player in self.game_state.players:
            #
            # Update the AFTER of this turn and calculate the final outcome
            #
            turn_history = player.turn_history
            player_info = player.player_info(include_successFormula=True, outputFormat="dict", include_degrees=True)
            turn_number = self.game_state.turn_number
            turn_history.add_player_info(turn_number, TurnHistory.AFTER_KEY, player_info)
            turn_history.create_turn(turn_number)
            self.log_info(player.turn_history.to_JSON())

        return result
    
    def quit(self, initials:str) -> CommandResult:
        """A single player, identified by initials, leaves the game.
        """
        result = CommandResult(CommandResult.SUCCESS, "'quit' command not yet implemented", False)
        return result
    
    def save(self, how="json") -> CommandResult:
        """Save the current game state.
            Arguments: how - save format: 'json' or 'pkl' (the default).
            save('pkl') uses joblib.dump() to save the CareersGame instance to binary pickel format.
            This can be reconstituted with joblib.load()
        """
        return self._gameEngineCommands.save_game(self._game_filename_base, self.game_id, how=how)
    
    def location(self, who=None)->str:
        player = self.game_state.current_player if who is None else self.get_player(who)
        message =  player.get_location()
        return CommandResult(CommandResult.SUCCESS, message, False)
    
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
            if game_square.square_class is GameSquareClass.OCCUPATION:
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
        player = self.game_state.current_player
        if player.can_retire:
            # all editions use the same name for Holiday, SpringBreak etc.
            game_square = self._careersGame.find_border_square("Holiday")
            next_square_number = game_square.number
            result = self.goto(next_square_number)
        else:
            result = CommandResult(CommandResult.ERROR, "Sorry, you can't retire yet.", True)
        return result
    
    def bump(self, who:str) -> CommandResult:
        """The current player bumps another player occupying the same board square to Unemployment
            Note that it is possible to land on a square occupied by more than one player,
            for example if a player chooses NOT to bump that square will have 2 players.
            In any case the initials of the player to be bumped must be provided.
            Only a single player may be bumped even if there are more than one on the square.
        
        """
        player = self.game_state.current_player
        bumped_player = None
        for player_initials in player.can_bump:
            if player_initials == who:
                bumped_player = self.game_state.get_player_by_initials(player_initials)
        
        if bumped_player is None:
            result = CommandResult(CommandResult.ERROR, f'Player {who} cannot be Bumped')
        else:
            #
            # find the Unemployment square and place the bumped_player there
            # also set the is_unemployed flag and clear any pending actions
            #
            border_square = self._careersGame.find_border_square("Unemployment")
            result = border_square.execute(bumped_player)
        return result
    
    def bankrupt(self, who="me") -> CommandResult:
        """The current player declares bankruptcy.
            A bankrupt player looses all cash, experience and opportunity cards and essentially
            restarts the game with configured starting cash and salary, and positioned at the "Payday" square (border square 0).
            The player does retain occupation experience however including any and all college degrees.
        
        """
        if who == "me":
            player = self.game_state.current_player
        else:
            player = self.get_player(who)
        player.bankrupt_me()
        if self.game_state.number_of_players == 1:
            player.can_roll = True
        result = CommandResult(CommandResult.SUCCESS, f'{player.player_initials} has declared bankruptcy', False)
        return result
    
    def pay(self, amount_str:int|str, initials:str|None=None) -> CommandResult:
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
        amount = int(amount_str) if isinstance(amount_str, str) else amount_str
        player = self.game_state.current_player if initials is None else self.get_player(initials)
        game_square = self._careersGame.get_game_square(player.board_location)
        amt_needed = game_square.special_processing.compute_cash_loss(player)
        if player.cash >= amount:
            if player.is_sick or player.is_unemployed:
                if amt_needed <= amount:
                    player.add_cash(-amt_needed)
                    if player.is_sick:
                        player.is_sick = False
                    else:
                        player.is_unemployed = False
                    player.can_use_opportunity = True
                    message = f'{player.player_initials} paid {amt_needed} and may leave {game_square.name}'
                else:
                    message = f'{player.player_initials} paid {amount} but needs {amt_needed} and must stay in {game_square.name}'
            else:
                player.add_cash(-amount)
                player.add_savings(amount)
                message = f'{player.player_initials} deposited {amount} into savings'
            return CommandResult(CommandResult.SUCCESS, message, True)
        else:
            message = f'{player.player_initials} has insufficient funds to cover {amount} and must either borrow cash from another player or declare bankruptcy or remain in Hospital/Unemployment'
            return CommandResult(CommandResult.ERROR, message, False, next_action="bankrupt")
        
    def transfer(self, quantity_str:str, what:str, from_player_id:str) -> CommandResult:
        """Transfers cash, opportunities or experience cards from one player to the current player
            For example: "transfer 500 cash BDB" transfers 500 in cash from player RBD to me.
            Arguments:
                from_player_number - the from player_initials, number or name
                what - "cash", "opportunity", "experience"
                quantity - the amount of cash or number of experience/opportunity cards being transferred
        """
        qty = int(quantity_str)
        from_player = self.get_player(from_player_id)
        player = self.game_state.current_player
        if what == 'cash':
            if from_player.cash <= qty:
                result = CommandResult(CommandResult.ERROR, f"{from_player.player_initials} doesn't have {qty} to transfer")
            else:
                from_player.add_cash(-qty)
                player.add_cash(qty)
                result = CommandResult(CommandResult.SUCCESS, f'transfer {qty} {what} from {from_player.player_initials} complete', True)
        else:
            result = CommandResult(CommandResult.SUCCESS, f'transfer {qty} {what} from player# {from_player.player_initials}  not implemented yet, but soon!', True)
        return result
        
    
    def list(self, what='all', how='condensed') ->CommandResult:
        """List the Experience or Opportunity cards held by the current player
            Arguments: what - 'experience', 'opportunity', or 'all'
                how - display control: 'full', 'condensed'  (the default), or 'count'
            Returns: CommandResult.message is the stringified list of str(card).
                For Opportunity cards this is the text property.
                For Experience cards this is the number of spaces (if type is fixed), otherwise the type.
            
        """
        player = self.game_state.current_player
        return GameEngineCommands.list(player, what, how)
    
    def perform(self, what:str, how:str) -> CommandResult:
        player = self.game_state.current_player
        return GameEngineCommands.perform(player, what, how)

    def set(self, who:str, what:str, amount:int):
        """Sets number of hearts, stars or cash for a given player
            This command is most useful in setting starting params in a script file
            that is not dependent on the gameParameters file.
            Arguments:
                who - the player as identified by player_initials
                what - "hearts" or "hapiness", "stars" or "fame", "cash" or "money", "salary"
                amount - an integer
            Note that the 'set' command is not allowed in production game mode, only test or test_prod
        """
        result = CommandResult.SUCCESS
        message = f'who: {who}, what:{what}, amount:{amount}'
        player = self.get_player(who)
        if player is None:
            message = f'No such player: {who}'
            result = CommandResult.ERROR
        else:
            match(what):
                case "happiness" | "hearts":
                    player.happiness = amount
                case "fame" | "stars":
                    player.fame = amount
                case "cash" | "money":
                    player.cash = amount
                case "salary":
                    player.salary = amount
                case _:
                    result = CommandResult.ERROR
                    message = f'Cannot set {what}. what must be one of "hearts", "stars", "cash" or "salary"'
                    
        return CommandResult(result, message, True)
        
    def saved(self) -> CommandResult:
        """List the games saved by this installationId, if any
        
        """
        result = CommandResult(CommandResult.SUCCESS, "'saved' command not yet implemented, but soon!", False)
        return result    

    def load(self, game_id:str) -> CommandResult:
        """Load a previously saved game, identified by the game Id
        
        """
        result = CommandResult(CommandResult.SUCCESS, "'load' command not yet implemented, any day now!", False)
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
    
    def add(self, what, name, initials=None, player_id=None, email=None, cash=0, stars=0, hearts=0, playerType:str="human") -> CommandResult:
        """Add a new player to the Game OR add a degree to the current player or the player whose initials are provided.
    
        """
        if what == 'player':
            sf = SuccessFormula(stars=stars, hearts=hearts, money=cash)
            player_type = PlayerType[playerType.upper()]    # HUMAN or COMPUTER
            player = Player(name=name, initials=initials, player_id=player_id, email=email, playerType=player_type)
            
            player.success_formula = sf
            player.set_starting_parameters(cash=self.careersGame.game_parameters.get_param('starting_cash'), salary=self._careersGame.game_parameters.get_param('starting_salary') )
            player.add_hearts(self.careersGame.game_parameters.get_param('starting_hearts'))
            player.add_stars(self.careersGame.game_parameters.get_param('starting_stars'))
            player.game_type = self._careersGame.game_type
            
            self._careersGame.add_player(player)        # adds to GameState
            if player.number == 0:      # the first player can roll
                player.can_roll = True

            starting_experience = self.careersGame.game_parameters.get_param('starting_experience_cards')
            if starting_experience > 0:
                card_list = self.careersGame.experience_cards.draw_cards(starting_experience)
                player.add_experience_card(card_list)
                
            starting_opportunities = self.careersGame.game_parameters.get_param('starting_opportunity_cards')
            if starting_opportunities > 0:
                card_list = self._careersGame.opportunities.draw_cards(starting_opportunities)
                player.add_opportunity_card(card_list)
                
            message = player.to_JSON()

        else:    
            # adds a degree in the current (or named) player's degree programs
            # name is the name of the degree program
            player = self.game_state.current_player if initials is None else self.get_player(initials)
            result = self.add_degree(player, name)
            message = result.message
        
        self.log_info(message)
        return CommandResult(CommandResult.SUCCESS, message, False)
    
    def game_status(self) -> CommandResult:
        """Get information about the current game in progress and return in JSON format
        """
        message =  self.game_state.to_JSON()
        
        return CommandResult(CommandResult.SUCCESS, message, True)
    
    def create(self, edition, installationId, game_type, points, game_parameters_type="prod") -> CommandResult:
        """Create a new CareersGame.
            Arguments:
                edition - 'Hi-Tech' or 'UK' are the only editions currently supported
                installationId - uniquely identifies the game's creator. It must have a length >= 5.
                game_type - 'points', 'timed', or 'solo'
                game_parameters_type - 'test', 'prod' or 'custom'. This maps to the appropriate (game_mode)
                    gameParameters JSON file: gameParameters_prod.json, gameParameters_test.json
            Returns: 
                CommandResult
                    message - JSON game_id, installationId if successful, else an error message: "error":<details>
                    return_code - SUCCESS or ERROR
            If a game_id is not provided, one is created based on the installationId and current date/time. For example, "ZenAlien2013_20220918-135325-650634-47816"
        """
        
        assert installationId is not None and len(installationId) >= 5
        self._edition = edition
        self._installationId = installationId
        game_id = self.game_id
        #
        # Create the CareersGame instance and the GameEngineCommands
        #
        self._careersGame = CareersGame(self._edition, installationId, points, game_id, game_type=game_type, game_parameters_type=game_parameters_type)
        
        self._game_state = self._careersGame.game_state
        self._game_state.game_id = game_id
        self._gameEngineCommands = GameEngineCommands(self._careersGame)
        self._gameEngineCommands.debug = self.debug
        self.currency_symbol = self._careersGame.game_parameters.get_param("currency_symbol")
        
        message = f'{{"game_id":"{self.game_id}", "installationId":"{installationId}"}}'
        self.log_info(message)    # INFO
        self._plugins = self._careersGame.plugins
        return CommandResult(CommandResult.SUCCESS, message, True)
    
    def start(self) -> CommandResult:
        return self._start()
    
    def buy(self, what:str, qty_str:int|str, amount_str:int|str) -> CommandResult:
        """Buy a number of items for the current player.
            The buy command is associated with one of the action_squares, specifically the game square's specialProcessing processingType.
            
            Arguments:
                what - "hearts" | "stars" | "experience" | "insurance" | "opportunity"
                qty - how many to buy (adds to the player's score or card deck)
                amount - cash amount cost
            Returns:
                CommandResult.SUCCESS if the player can cover the cost, AND the action is appropriate for the player's current board location.
                otherwise CommandResult.ERROR with an appropriate error message.
                
            Okay to have a negative quantity and zero amount. For example, to lose 1 heart send: "buy hearts -1 0"
        """
        player = self.game_state.current_player
        return self._buy(player, what, qty_str, amount_str)
    
    def resolve(self, what:str, choice, **kwargs ) -> CommandResult:
        """Resolve a player's pending_action.
            Arguments:
                what - the pending_action that needs resolution, for example "select_degree"
                choice - the player's choice, for example for what=="select_degree", choice is the degree name, like "Marketing"
                        This can also be an amount/quantity to apply. For example: resolve buy_hearts 4 (buy 4 hearts).
                
            Returns: CommandResult
           Note that border and occupation squares may have a pending_action. See GameConstants.PendingActionType
               for a complete list.
               gamble - requires an amount
               select_degree - choice is a DegreeProgram
               resolve back_stab_or_not <opponent player's initials> or no
               
        """
        message = f'{what}:{choice}'
        player = self.game_state.current_player
        game_square = self.get_player_game_square(player)
        pending_action = None
        
        if what == "*" and player.pending_actions.size() > 0:    # resolve the most recently added PendingAction
            pending_action = player.pending_actions.get(-1)      # does not remove from the player's pending actions list
            what = pending_action.pending_action_type.value
            
        else:
            pending_action = player.pending_actions.find(what)     # does not remove from the player's pending actions list
            
        if pending_action is not None:
            pending_game_square_name = pending_action.pending_game_square_name
            pending_game_square = None if pending_game_square_name is None else self.careersGame.find_border_square(pending_game_square_name)
            
            if what == PendingActionType.SELECT_DEGREE.value:  # the degree program chosen is the 'choice'
                result = self.add_degree(player, choice)
                result.message = f'{message}\n{result.message}'

            elif what ==  PendingActionType.GAMBLE.value:
                #
                # execute the special processing for the Gamble game square
                #
                result = pending_game_square.execute_special_processing(player)

            elif what ==  PendingActionType.BUY_HEARTS.value:
                result = pending_game_square.execute_special_processing(player, choice=choice, what='hearts')
            
            elif what ==  PendingActionType.BUY_EXPERIENCE.value:
                amounts = pending_game_square.special_processing.amount_dict
                ncards = str(choice)
                if ncards in amounts:
                    cost = amounts[ncards]
                    if cost <= player.cash:
                        player.add_cash(-cost)
                        # draw that number of cards
                        for i in range(1,choice+1):
                            acard = self.careersGame.experience_cards.draw()
                            player.add_experience_card(acard)
                        result = CommandResult(CommandResult.SUCCESS, f'{ncards} Experience cards added for {self.currency_symbol}{cost}', True)
                    else:
                        result = CommandResult(CommandResult.ERROR, f"You can't afford {ncards} Experience cards. Try again.", False)
                else:
                    result = CommandResult(CommandResult.ERROR, f'{choice} is an invalid selection. Valid selections and costs are {amounts}', False)
                
            elif what ==   PendingActionType.BUY_STARS.value:
                result = pending_action.pending_game_square.execute_special_processing(player, choice=choice, what='stars')
            
            elif what ==   PendingActionType.BUY_INSURANCE.value:    # assume 1 quantity, regardless of the quantity specified
                amount = game_square.special_processing.amount
                result = self.buy("insurance", choice, amount)
            
            elif what ==   PendingActionType.STAY_OR_MOVE.value:    # choices: stay, move
                if choice.lower() == "stay":
                    result = game_square.execute(player)
                else:   # move off Holiday
                    player.on_holiday = False
                    result = self.roll(player, pending_action.pending_dice)
                    
            elif what == PendingActionType.BANKRUPT.value:          # choices: yes (to declare bankruptcy), no
                if choice.lower() == "yes":
                    result = self.bankrupt()
                else:
                    result = CommandResult(CommandResult.SUCCESS, 'You elected not to declare bankruptcy at this time', True)
                 
            elif what ==   PendingActionType.TAKE_SHORTCUT.value:   # yes=take the shortcut
                if choice.lower() == "yes":
                    #
                    # place the player's board location to the space BEFORE the next_square in the
                    # shortcut specialProcessing
                    #
                    player.board_location.occupation_square_number = game_square.special_processing.next_square - 1
                    result = CommandResult(CommandResult.SUCCESS, 'You elected to take the shortcut on your next move', True)
                    #self._goto(pending_action.pending_amount, player)
                else:
                    result = CommandResult(CommandResult.SUCCESS, 'You elected not to take the shortcut on your next move', True)
                    
            elif what ==   PendingActionType.BACKSTAB.value:
                # resolve backstab_or_not   yes|no  <1 or more player_initials>
                #
                if 'player_initials' in kwargs:
                    player_initials = kwargs['player_initials'].split()    # space delimited string of player's initials
                else:
                    player_initials = [choice]
                    # the named player must have completed the associated occupation
                    # or is currently in the occupation
                if player_initials is None:
                    result = CommandResult(CommandResult.ERROR, "You must specify the player(s) to back stab", True)
                elif 'no' in player_initials:
                    result = CommandResult(CommandResult.SUCCESS, 'You elect not to back stab another player. Good for you!', True)
                else:
                    message = ""
                    for initials in player_initials:
                        other_player = self.get_player(initials)
                        if other_player is None:
                            result = CommandResult(CommandResult.ERROR, f'No such player: {initials}', True)
                        else:
                            occupation =self.careersGame.get_occupation(player.current_occupation_name())
                            occupation_square = occupation.occupationSquares[player.board_location.occupation_square_number]
                            can_backstab = self._gameEngineCommands.can_backstab_player(player, other_player, occupation)
                            if not can_backstab:
                                result = CommandResult(CommandResult.ERROR, f'You cannot back stab "{initials}"', True)
                            else:
                                # player doing the backstabbing loses 4 hearts FOR EACH player he/she back stabs!
                                #
                                player.add_hearts(occupation_square.hearts)    # this will be <0
                                hearts_loss = occupation_square.special_processing.amount
                                other_player.add_hearts(hearts_loss)    # this will be <0
                                message += \
                            f'{player.player_initials} back stabs {other_player.player_initials} who loses {-hearts_loss} Hearts. You lose {-occupation_square.hearts}\n'
                                result = CommandResult(CommandResult.SUCCESS, message, True)
                    
            elif what ==   PendingActionType.CASH_LOSS_OR_UNEMPLOYMENT.value:
                #
                # the player can afford the amount - question is what is their choice? 
                # pay or go (to unemployment)
                #
                self.log_info(f'{player.player_initials} resolve {what} choice is "{choice}"')
                if choice.lower() == 'pay':
                    amount = game_square.special_processing.amount
                    player.add_cash(-amount)
                    player.add_point_loss("cash", amount)    # loss is insurable
                    result = CommandResult(CommandResult.SUCCESS, f'You paid {amount} to avoid Unemployment', True)
                else:    # go to Unemployment
                    result = self.goto("Unemployment")

            elif what ==   PendingActionType.CHOOSE_OCCUPATION.value:
                # choice is the occupation name
                game_square = self._careersGame.find_border_square(choice)
                if game_square is None or game_square.square_type is not BorderSquareType.OCCUPATION_ENTRANCE_SQUARE:
                    result = CommandResult(CommandResult.ERROR, f'There is no Occupation named {choice}', False)
                else:
                    # can't use this to choose College - must be an occupation
                    sp_type = game_square.special_processing.processing_type
                    if sp_type is SpecialProcessingType.ENTER_COLLEGE:
                        result = CommandResult(CommandResult.ERROR, "You cannot choose College. Your choice must be an Occupation", False)
                        # player keeps the card
                        player.add_opportunity_card(player.opportunity_card)
                    else:
                        occupation = self._careersGame.get_occupation(game_square.name)
                        can_enter = self._gameEngineCommands.can_enter(occupation, player)
                        can_move = not (player.is_sick or player.is_unemployed)
                        if can_enter and can_move:
                            #
                            # advance the occupation square and immediately enter
                            #
                            result1 = self._goto(game_square.number, player)
                            result2 = self.enter(occupation.name)
                            result = CommandResult(CommandResult.SUCCESS, f'{result1.message}\n{result2.message}', True)
                        else:
                            result = CommandResult(CommandResult.ERROR, f'You can afford the {self.currency_symbol}{occupation.entry_fee} for {occupation.name}', False)

            else:
                result = CommandResult(CommandResult.ERROR, f'Sorry {player.player_initials}, "{what}" is an invalid or unimplemented pending action!', False)


        else:
            result = CommandResult(CommandResult.ERROR, f'Nothing to resolve for {what}', False)

        #
        # clear pending_action for all except SELECT_DEGREE if result is SUCCESS
        #            
        if result.is_successful() and not player.on_holiday:
            if pending_action.pending_action_type is PendingActionType.SELECT_DEGREE:
                player.clear_pending()
            else:
                player.clear_pending(PendingActionType.SELECT_DEGREE)
        return result
        
                    
    #####################################
    #
    # Game engine action implementations
    #
    #####################################
        
    def _start(self) -> CommandResult:
        message = f'Starting game {self.game_id}'

        self.log_info(message)
        self.game_state.set_next_player()    # sets the player number to 0 and the curent_player Player reference
        self._careersGame.start_game()       # sets the start datetime
        #
        # run any "start" plug-ins
        #
        plugins = self._plugins["start"]     # a List of Plugin class instances to run
        for plugin_instance in plugins:
            result = plugin_instance.run()   # start plugins apply to all players
            self.log_info(result)
                
        return CommandResult(CommandResult.SUCCESS, message, True)
    
    def _buy(self, player:Player, what:str, qty_arg:int|str=1, amount_arg:int|str=1) -> CommandResult:
        """Implements the buy command
            Arguments:
                player - the current or affected player reference
                what - "hearts" | "stars" | "experience" | "insurance" | "opportunity"
                qty - how many to buy (adds to the player's score or card deck). May be an int or str
                amount - cash amount cost. May be an int or str
             The player must have the appropriate pending_action in order to be valid
             and it must match the current location's special processing type value
             (if the current board location HAS specialProcessing)
        """
        amount = int(amount_arg)
        qty = 1 if qty_arg is None else int(qty_arg)

        if player.cash < amount:
            return CommandResult(CommandResult.ERROR, f'Insufficient funds {self.currency_symbol}{player.cash} for amount {self.currency_symbol}{amount}', True)
    
        game_square = self.get_player_game_square(player)
        special_processing = game_square.special_processing  # could be None or empty

        sp_pending_action = special_processing.pending_action
        pending_action = None
        pa_string = f'buy_{what}'
        for pa in player.pending_actions.get_all():
            if pa.pending_action_type.value.lower() == pa_string:
                pending_action = player.pending_actions.get_pending_action(pa.pending_action_type, remove=True)
                break
        
        if pending_action is None or (sp_pending_action is not None and pa_string != sp_pending_action.value.lower()):
            return CommandResult(CommandResult.ERROR, f'Cannot buy {qty} "{what}" here', False)
        
        player.add_cash(-amount)
        if what.lower().startswith('heart'):    # buy Hearts (Happiness)
            player.add_hearts(qty)

        elif what.lower().startswith('star'):   # buy Stars (Fame)
            player.add_stars(qty)

        elif what.lower().startswith('exp'):    # buy Experience card(s)
            self.add_experience_cards(player, qty)
            
        elif what.lower().startswith('opp'):    # buy Opportunity card(s)
            self.add_opportunity_cards(player, qty)

        elif 'insurance' in what.lower():    # buy insurance, okay to buy more than 1 policy
            total_amount = qty * amount
            if player.cash < total_amount:
                return CommandResult(CommandResult.ERROR, f'Insufficient funds {self.currency_symbol}{player.cash} for insurance amount {self.currency_symbol}{amount}', True)
            player.is_insured = True

        elif what.lower() == 'gamble':    # player needs to roll 2 dice in order to gamble - that's a separate command
            return CommandResult(CommandResult.SUCCESS, "", False)
        else:
            return CommandResult(CommandResult.ERROR, f'Cannot buy {qty} {what} here', False)
        
        return CommandResult(CommandResult.SUCCESS, f'{qty} {what} added', True)


    
    def _execute_opportunity_card(self,  player:Player, opportunityCard:OpportunityCard=None, spaces:int|str|None=None) -> CommandResult:
            
            result = self._gameEngineCommands.execute_opportunity_card(player, opportunityCard, dest=spaces)
            if result.is_successful():
                player.opportunity_card = opportunityCard
            #
            # If there is a next_action, then execute it
            #
            self._execute_next_action(player, result)
            player.used_opportunity()
            return result                   
    
    def _execute_experience_card(self,  player:Player, experienceCard:ExperienceCard, spaces:int|str|None=None) -> CommandResult:
        '''Executes an Experience card.
            Command format is "use experience [roll]"
            roll is required only for wild cards and specifies the dice as a csv list, for example "4,5" to roll a 9, or "3" as a single die roll
            If the experience is a wild card, it must be appropriate to the class of the current_game square.
            one_die_wild - can only be used when the player is on an occupation square
            two_die_wild - can only be used on a border square
            triple_wild - can be used in both
            Arguments:
                player - the current Player
                experienceCard - the ExperienceCard being played
                spaces - applies to wild cards only (?, ??, ???) the roll to apply.
                         For ONE_DIE_WILD, this a string with numerical value from 1 to 6 inclusive,
                         for TWO_DIE_WILD this is a comma-delimited string representing the 2 die, for example "2,5"
                         for TRIPLE_WILD, this can be either depending on the player's board position.
            Note - _execute_experience_card(...) is implemented by roll() which in turn is implemented by _advance().
            
        '''
        player.experience_card = experienceCard
        nspaces = experienceCard.spaces
        game_square = self.get_player_game_square(player)    # determines what wild card is valid
        board_location = player.board_location
        roll = str(spaces) if spaces is not None else None   # for wild cards roll can be an int or a str
        
        if experienceCard.card_type is ExperienceType.FIXED:   # could be negative for moving backwards
            dice = [nspaces]
        else:    # must be a wild card - ?, ?? or ???
            #
            # If the player has done an enter but not yet rolled:
            game_square_class = game_square.square_class if board_location.occupation_name is None else GameSquareClass.OCCUPATION
            
            if game_square_class is GameSquareClass.OCCUPATION and experienceCard.card_type is ExperienceType.TWO_DIE_WILD or \
               game_square_class is GameSquareClass.BORDER and experienceCard.card_type is ExperienceType.ONE_DIE_WILD:
                message = f'Experience type {experienceCard.card_type.value} cannot be used for {game_square.square_class.value} '
                self.log_info(message)
                return CommandResult(CommandResult.ERROR, message, False)
            else:   # simulate a roll of 1 or 2 die
                if spaces is None:
                    message = f'A roll must be specified for {experienceCard.card_type.value}'
                    self.log_info(message)
                    return CommandResult(CommandResult.ERROR, message, False)
                else:
                    die = roll.split(',')
                    ndie = len(die)
                    if ndie == 1 and experienceCard.card_type is ExperienceType.TWO_DIE_WILD or \
                       ndie == 2 and experienceCard.card_type is ExperienceType.ONE_DIE_WILD:
                        message = f'Roll {die} cannot be applied to {experienceCard.card_type.value}'
                        self.log_info(message)
                        return CommandResult(CommandResult.ERROR, message, False)
                                     
                dice = [int(c) for c in die]
                nspaces = sum(dice)
                    
        message = f'{player.player_initials} roll: {dice}, moving: {nspaces} spaces'
        self.log_info(message)
        result = self.roll(player, dice)
        #
        # remove the used experience from the player's deck
        #
        player.used_experience()
            
        return result        
    
    def execute_game_square(self, player:Player, board_location:BoardLocation) -> CommandResult:
        """Executes the actions associated with a given BoardLocation and Player
        
        """
        game_square = self.get_player_game_square(player)
        if board_location.occupation_name is not None:
            result = self._execute_occupation_square(player, game_square, board_location)
        else:
            result = self._execute_border_square(player, game_square, board_location)
            
        #
        # if there is a next action to perform then do it
        #
        self._execute_next_action(player, result)
        return result
        
    def _execute_occupation_square(self, player:Player, game_square:OccupationSquare, board_location:BoardLocation) -> CommandResult:
        message = f'execute_occupation_square {board_location.occupation_name}  {board_location.occupation_square_number} for {player.player_initials}'
        self.log_info(message)
        result = game_square.execute(player)
        
        return result
    
    def _execute_border_square(self, player:Player, game_square:BorderSquare, board_location:BoardLocation) -> CommandResult:
        message = f'{player.player_initials} landed on {game_square.name}  ({board_location.border_square_number})'
        self.log_info(message)
        result = game_square.execute(player)
        result.message = message + "\n" + result.message

        return result
    
    def _execute_next_action(self, player:Player, current_result:CommandResult) -> CommandResult:
        """If current_result has a next action to perform then execute it with execute_command.
        """
        next_action = current_result.next_action
        if next_action is not None:
            action_result = self.execute_command(next_action, player)
            current_result.message = current_result.message + "\n" + action_result.message
            current_result.return_code = action_result.return_code
            current_result.done_flag = action_result.done_flag
        return current_result

    def _get_next_square_number(self, player:Player, num_spaces:int) -> int:
        """Gets the next square number given the number of spaces to advance.
            Arguments:
                player - the Player
                num_spaces - the number of spaces to advance. abs(num_spaces) Must be >0 to go anywhere, but this doesn't check.
                    If num_spaces <0, this is a move backwards.
                    
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
        if self.is_in_occupation(game_square, player):
            if game_square.special_processing is not None and game_square.special_processing.next_square is not None:
                next_square_number = game_square.special_processing.next_square + num_spaces - 1
            else:
                next_square_number = board_location.occupation_square_number + num_spaces    # could be > size of the occupation, that's handled by goto()
        else:
            next_square_number = board_location.border_square_number + num_spaces        # could be > size of the board, that's also handled by goto()
            
        return next_square_number

    def goto(self, square_ref:int|str,  starting_square_number:int=0) -> CommandResult:
        """Immediately place the designated player on the designated BorderSquare OR OccupationSquare and execute that square.
            If the current player is in an occupation, this places the player on square_number of that Occupation.
            Otherwise, the square_ref refers to a BorderSquare name or number.
            NOTE that the border square number could be out of range. i.e. > game size. 
            If so, the square number adjusted and then the pass_payday() action is executed.
            
            NOTE that when in an Occupation the designated square_number could be out of range. i.e. > the occupation exit_square_number.
            If so, the player is advanced to the next BorderSquare and the exit occupation logic is executed.
            
        """
        player = self.game_state.current_player
        square_number = square_ref
        if isinstance(square_ref, str):
            bs = self._careersGame.find_border_square(square_ref, starting_square_number)
            if bs is None:
                return CommandResult(CommandResult.ERROR, f"No such destination: '{square_ref}' ", True)

            square_number = bs.number
            player.board_location.occupation_name = None    # leaving the occupation (if in one) to go to a BorderSquare

        return self._goto(square_number, player)    

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
        if self.is_in_occupation(game_square, player):        # If player is starting or currently in or completing an Occupation
            
            occupation_name =  player.board_location.occupation_name
            occupation = self._careersGame.occupations[occupation_name]
            if square_number >= occupation.size:
                
                exit_result =  self.exit_occupation(player, board_location)
                
                #
                # go to next border square and update board_location after the occupation exit
                #
                board_location.border_square_number = square_number - occupation.size + occupation.exit_square_number
                board_location.occupation_name = None
                game_square =  self._careersGame.get_border_square(board_location.border_square_number)
                board_location.border_square_name = game_square.name                
                
                result = self.execute_game_square(player, board_location)
                result.message = exit_result.message + "\n" + result.message

            else:    # next square is in this occupation
                board_location.occupation_square_number = square_number
                result = self.execute_game_square(player, board_location)
                
        else:   # goto designated border square. Possible that square_number == the player's current position
                # in that case the player stays on that space. For example, on Holiday and they choose to stay put.
                # need to take into account if the player moved backwards using an Experience card
            moved_backwards = True if player.experience_card is not None \
                and player.experience_card.card_type is ExperienceType.FIXED \
                and player.experience_card.spaces < 0 else False
            current_square_number = board_location.border_square_number
            board_size = self._careersGame.game_board.game_layout_dimensions['size']   # total number of squares, 42 is typical
            if square_number < 0:
                square_number = board_size + square_number
            if square_number >= 0 and \
               square_number < board_size and \
               (square_number >= current_square_number or (square_number < current_square_number and moved_backwards)):
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
                if border_square.square_type is BorderSquareType.TRAVEL_SQUARE and self.was_prior_travel(player):
                    result = CommandResult(CommandResult.SUCCESS, "", True)
                else:
                    result = self.execute_game_square(player, board_location)

            else:    # player passed or landed on Payday
                if square_number >  board_location.border_square_number :
                    square_number = square_number - self._careersGame.game_board.game_board_size
                if square_number >= board_size:
                    result =  CommandResult(CommandResult.ERROR, f'{square_number} is not a valid destination', True)
                else:    
                    border_square = self._careersGame.get_border_square(square_number)
                    board_location.border_square_number = square_number
                    board_location.border_square_name = border_square.name
                    #
                    # do not pass Payday if the destination is Unemployment
                    #
                    if border_square.special_processing.processing_type is SpecialProcessingType.HOSPITAL:
                        payday_result = CommandResult(CommandResult.SUCCESS, "Do not pass Payday. Go directly to the Hospital", True)
                    elif border_square.special_processing.processing_type is SpecialProcessingType.UNEMPLOYMENT:
                        payday_result = CommandResult(CommandResult.SUCCESS, "Do not pass Payday. Go directly to Unemployment", True)
                    else:
                        payday_result = self.pass_payday(player)
                    #
                    # again, check travel arrangements
                    #
                    if border_square.square_type is BorderSquareType.TRAVEL_SQUARE and self.was_prior_travel(player):
                        result = CommandResult(CommandResult.SUCCESS, "", True)
                    elif square_number > 0:
                        result = self.execute_game_square(player, board_location)
                
                    if result is None:
                        result = payday_result
                    else:
                        result.message = f'{payday_result.message}\n{result.message}'
        #
        # if another player is on that square AND the square is NOT Unemployment, they can be bumped
        #
        other_players = self.who_occupies_my_square(player)
        if player.current_border_square_name() != "Unemployment":
            if len(other_players) > 0:
                result.message = result.message + f'\n{player.player_initials} can bump {other_players}'
        player.can_bump = other_players   # could be an empty list
        return result

    def exit_occupation(self, player:Player, board_location:BoardLocation) -> CommandResult:
        """Applies exiting an occupation rules when a player exits an occupation path.
            Arguments:
                player - the current player
                board_location - BoardLocation
            Returns:
                CommandResult. If exiting college, choices is set to the list of degree programs to select from.
                        pending_action is set to the border_square pending_action (if there is one).
                        For college this is "select_degree"
                        
            Exiting can be done by rolling out, using an Experience, or using an Opportunity to go somewhere else.
            The occupation could be College ("occupationClass" : "college") or a regular Occupation ("occupationClass" : "occupation")
            * if the player entered the Occupation via Opportunity card, that card is removed from the player's hand
            * if the player completed the Occupation, credit is applied to the player's occupation record and up to 3 Experience cards given
            * if the player has completed 3 trips through a regular Occupation, the player's can_retire flag is set to True

            Note that exit_occupation does NOT update the player's board position.  
            That is done by goto() which calls this method before updating the board position.
            So upon entry, border square location is the occupation entrance square for this occupation (or college).
            Note also that the player's salary is NOT adjusted when completing college. That is done by the add_degree() method.
            
        """
        nexperience = 0
        trips = 1
        choices = None    # if exiting College, this is a list of degree programs to select from
        if board_location.occupation_name in player.occupation_record:
            trips = player.occupation_record[board_location.occupation_name] + 1  # number of trips not counting this one
            player.occupation_record[board_location.occupation_name] = trips
            
        else:
            player.occupation_record[board_location.occupation_name] = trips
        if trips >= 3:
            #
            # player can retire
            #
            player.can_retire = True
        #
        # No experience given for completing College
        # 
        game_square = self._careersGame.get_border_square(board_location.border_square_number)
        sptype = game_square.special_processing.processing_type
        if sptype == SpecialProcessingType.ENTER_OCCUPATION:
            if trips <= 3:  # at most 3 experience cards can be given
                nexperience = trips
            else:
                nexperience = 3

            self.add_experience_cards(player, nexperience)
            message = f'{player.player_initials} Leaving {board_location.occupation_name}, collects {nexperience} Experience cards'
        else:    
            # special_processing.processing_type == SpecialProcessingType.ENTER_COLLEGE
            # player must choose a degree program
            # salary increase is dependent on the # of degrees earned in that degree program
            player.add_pending_action(PendingActionType.SELECT_DEGREE, game_square_name=game_square.name)
            choices = self._careersGame.college_degrees["degreePrograms"]
            message = f'{player.player_initials} Leaving {board_location.occupation_name}, pending_action: {PendingActionType.SELECT_DEGREE.value}'
        
        self.log_info(message)
        result = CommandResult(CommandResult.SUCCESS, message, True, choices=choices)
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
        self.log_info(result.message)
        return result
    
    def was_prior_travel(self, player) -> bool:
        """Returns True if the player's prior border position was a travel square, False otherwise
            This is needed in order to avoid endless travel hops.
        """
        result = False
        ps = player.board_location.prior_border_square_number
        if ps is not None and self._careersGame.game_board.border_squares[ps].square_type is BorderSquareType.TRAVEL_SQUARE:
            result = True
        return result
        
    def add_degree(self, player:str|Player, degree_program) -> CommandResult:
        """Adds a degree to the player and adjusts the salary as needed.
            The maximum number of degrees a player can have in any degree program is "maxDegrees".
            Player's Salary is not adjusted if their number of degrees exceeds that.
            The player's pending_action is also reset if it's PendingActionType.SELECT_DEGREE
              Arguments:
                  player - a Player instance OR initials (str)
                  degree_program - the name of the degree program for this game edition.
        """
        thePlayer = player
        if isinstance(player, str):
            thePlayer = self._game_state.get_player_by_initials(player)
        
        game_degrees = self._careersGame.college_degrees
        degree_names = game_degrees['degreeNames']
        degreeProgram = degree_program.title()   # case matters!
        if degreeProgram not in game_degrees['degreePrograms']:   
            return CommandResult(CommandResult.ERROR, f"No such degree program: {degreeProgram}", False)
        
        max_allowed = game_degrees['maxDegrees']
        salary_increases = game_degrees['salaryIncreases']
        my_degrees = thePlayer.my_degrees
        ndegrees = 0
        salary_inc = 0
        if degreeProgram in my_degrees:
            ndegrees = thePlayer.my_degrees[degreeProgram]
        
        if ndegrees == 0:
            thePlayer.my_degrees[degreeProgram] = 1
            salary_inc = salary_increases[0]
            thePlayer.salary = thePlayer.salary + salary_inc   # automatically adds to salary_history
            
        elif ndegrees + 1 <= max_allowed:
            salary_inc = salary_increases[ndegrees]
            thePlayer.my_degrees[degreeProgram] = ndegrees + 1
            thePlayer.salary = thePlayer.salary + salary_inc
        
        else:
            ndegrees = 3  # already maxed out
        
        message = f'{thePlayer.player_initials} awarded {degree_names[ndegrees]} degree in {degreeProgram}'
        if salary_inc > 0:
            symbol = self._careersGame.game_parameters.get_param('currency_symbol')
            message += f' and a Salary increase of {symbol}{salary_inc}'

        return CommandResult(CommandResult.SUCCESS, message, True)
        
    def who_occupies_my_square(self, player) -> List[str]:
        """If the game square currently occupied by player is also occupied by another player(s), return those players.
            The player landing on an occupied square may bump that player to Unemployment.
            Arguments: 
                player - the Player landing on the designated square
            Returns: a list of Player initials on the square occupied by player, or an empty list if none.
        """
        plist = []
        #occupation_name = player.current_occupation_name()      # could be None
        my_location = player.get_location()
        for ap in self._game_state.players:
            if player.number == ap.number:
                continue    # it's me!
            ap_location = ap.get_location()
            if ap_location == my_location:
                plist.append(ap.player_initials)
                
        return plist
    
    def is_in_occupation(self, game_square:GameSquare, player:Player) -> bool:
        """Check if a Player is entering or inside an Occupation path
            Return: True if the game square Player is on has square_class of 'occupation',
            in which case they are inside the Occupation.
            Or they are at the entrance square of an Occupation they are entering.
        """
        return game_square.square_class is GameSquareClass.OCCUPATION or \
            (player.board_location.occupation_name is not None and player.board_location.occupation_name==game_square.name)
    
    def _resolve_pending(self, player:Player):
        '''Is there a pending action for this player? This might include a pending penalty.
            clear pending_action, pending_amount, pending_game_square and pending_dice
        '''
        game_square = self._careersGame.get_game_square(player.board_location)
        if player.has_pending_actions():
            sp_type = game_square.special_processing.processing_type.value
            pending_action = player.pending_actions.get_pending_action(sp_type, remove=False)
            if pending_action is not None:
                if game_square.special_processing.penalty > 0:
                    if pending_action.pending_action_type.value == SpecialProcessingType.BUY_HEARTS.value and player.happiness > 0:
                        player.add_hearts(-game_square.special_processing.penalty)

                        player.clear_pending(pending_action.pending_action_type)
    
if __name__ == '__main__':
    print(CareersGameEngine.__doc__)
    
    