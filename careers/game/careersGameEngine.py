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

from datetime import datetime
import random



class CareersGameEngine(object):
    """CareersGameEngine executes the action(s) associated with each player's turn.
    Valid commands + arguments:
        command :: <roll> | <use> | <retire> | <bump> | <bankrupt> | <list> | <status> | <quit> | <done> | <end game>
                     | <saved games> | <save> | <load> | <query> | <enter> | <goto> | <add> | <use insurance>
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
        <enter> :: "enter" <occupation_name> [<square_number>]          ;enter occupation at occupation square square_number
        <goto> :: "goto" <square_number>                                ;go to border square square_number
        <add> :: "add" player_name player_initials cash stars hearts    ;adds a new player to the game
        <use insurance> :: "use_insurance"
    """
    
    COMMANDS = ['roll', 'use', 'goto', 'enter', 'status', 'done', 'next', 'end', 'quit', 'save', 'where', \
                'retire', 'bump', 'bankrupt', 'list', 'saved', 'load',  'who', 'add']
    
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
        self._admin_player = Player(number=-1, name='Administrator', initials='admin')
    
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

    def execute_command(self, command:str, aplayer:Player, args:list=[]):
        """Executes a command for a given Player
            Arguments:
                command - the command name, for example "roll"
                args - a possibly empty list of additional string arguments
                player - a Player reference. If none, admin_player is used.
            Returns: a CommandResult object. The player's current board_location is always returned in the CommandResult
            See game.CommandResult for details
        
        """
        player = aplayer
        if aplayer is None:
            player = self._admin_player
            
        self.log(f'{player.player_initials}: {command} {args}')
        if command is None or len(command) == 0:
            return CommandResult(CommandResult.SUCCESS, "", False)
        cmd_result = self._evaluate(command, args)
        
        board_location = player.board_location    # current board location AFTER the command is executed
        self.log(f'  {player.player_initials} results: {cmd_result.return_code} {cmd_result.message}\n{board_location}')
        cmd_result.board_location = board_location
        return cmd_result
        
    def _evaluate(self, commandTxt, args=[]) -> CommandResult:
        """Evaulates a command string with eval()
            Arguments:
                commandTxt - the command name + any arguments to evaluate.
                args - an optional list of additional arguments
            Returns - a CommandResult
        """
        command_result = self._parse_command_string(commandTxt, args)
        if command_result.return_code != CommandResult.SUCCESS:     # must be an error
            return command_result
        
        command = "self." + command_result.message
        command_result = None
        print("execute " + command)
        try:
            command_result = eval(command)
        except Exception as ex:
            command_result = CommandResult(CommandResult.ERROR,  f'"{command}" : Invalid command format or syntax',  False, exception=ex)
            raise ex
        return command_result
        
    def _parse_command_string(self, txt, addl_args=[]) -> CommandResult:
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
    
    def get_player(self, pid, pnumber=None):
        """Gets a Player by initials, name, or number
        
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
    def roll(self, number_of_dice=2):
        """Roll 1 or 2 dice and advance that number of squares for current_player and execute the occupation or border square.
        """
        done = False
        player = self.game_state.current_player
        ndice = number_of_dice
        game_square = self.get_player_game_square(player)       # could be BorderSquare or OccupationSquare
        in_occupation = False
        board_location = player.board_location

        if game_square.square_class == 'occupation':    # then I am on an occupation path so roll 1 die
            ndice = 1
            in_occupation = True
        
        dice = random.choices(population=[1,2,3,4,5,6], k=ndice)
        total = sum(dice)
        
        self.log(f' {player.player_initials}  rolled {total} {dice}')
        #
        # advance that number of spaces if permitted to do so
        # 
        if in_occupation:
            next_square_number = board_location.occupation_square_number + total    # could be > size of the occupation, that's handled by goto()
        else:
            next_square_number = board_location.border_square_number + total        # could be > size of the board, that's also handled by goto()
            
        result = self.goto(next_square_number)
        return result
    
    def use(self, what, card_number, spaces=0):
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
            thecard = cards.get(card_number, None)
            if thecard is None:    # no such card
                result = CommandResult(CommandResult.ERROR, f"No {what} card exists with number {card_number} ", False)
            else:
                result = self.execute_card(player, opportunityCard=thecard)
        elif what.lower() == 'experience':
            cards = player.get_experience_cards()   # dict with number as the key
            thecard = cards.get(card_number, None)
            if thecard is None:    # no such card
                result = CommandResult(CommandResult.ERROR, f"No {what} card exists with number {card_number} ", False)
            else:
                result = self.execute_card(player, experienceCard=thecard, spaces=spaces)
        else:
            result = CommandResult(CommandResult.ERROR, f"use can't use a '{what}' ", False)
        return result
    
    def use_insurance(self):
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
        
    def goto(self, square_number):
        """Immediately place the current player on the designated BorderSquare OR OccupationSquare and execute that square.
            If the current player is in an occupation, this places the player on square_number of that Occupation.
            Otherwise, the square_number refers to a BorderSquare.
            NOTE that the border square number could be out of range. i.e. > game size. 
            If so, the square number adjusted and then the pass_payday() action is executed.
            NOTE that when in an Occupation the designated square_number could be out of range. i.e. > the occupation exit_square_number.
            If so, the player is advanced to the next BorderSquare and the exit occupation logic is executed.
            
        """
        player = self.game_state.current_player
        game_square = self.get_player_game_square(player)
        board_location = player.board_location
        result = None
        if game_square.square_class == 'occupation':
            
            occupation_name =  player.board_location.occupation_name
            occupation = self._careersGame.occupations[occupation_name]
            if square_number >= occupation.size:
                #
                # go to next border square after the occupation exit
                #
                board_location.border_square_number = square_number - occupation.size + occupation.exit_square_number - 1
                board_location.occupation_name = None
                game_square =  self._careersGame.get_border_square(board_location.border_square_number)
                board_location.border_square_name = game_square.name
                exit_result =  self.exit_occupation(player, board_location)
                result = self.execute_game_square(player, board_location)
                result.message = exit_result.message + "\n" + result.message
                return result
            else:    # next square is in this occupation
                board_location.occupation_square_number = square_number
                return self.execute_game_square(player, board_location)
                
        else:   # goto designated border square
            if square_number >= 0 and square_number <= self._careersGame.game_board.game_layout_dimensions['size']:
                player = self.game_state.current_player
                border_square = self._careersGame.get_border_square(square_number)
                board_location.border_square_number = square_number
                board_location.border_square_name = border_square.name
                board_location.occupation_name = None
                #
                # execute this game square
                #
                result = self.execute_game_square(player, board_location)
                return result
            else:    # player passed or landed on Payday
                square_number = square_number - self._careersGame.game_board.game_board_size - 1
                border_square = self._careersGame.get_border_square(square_number)
                board_location.border_square_number = square_number
                board_location.border_square_name = border_square.name
                payday_result = self.pass_payday(player, board_location)
                result = self.execute_game_square(player, board_location)
                result.message = payday_result.message + "\n" + result.message
                return result
                
        return result
    
    def enter(self, occupation_name, square_number=None):
        """Enter the named occupation at the designated square number and execute the occupation square.
            This checks if the player meets the entry conditions
            and if not, return an error with the appropriate message.
            Upon entering, the player's BoardLocation  occupation_name is set to occupation_name,
            and border_square_number = current border_square_number.
            Arguments:
                occupation_name - the name of the occupation to enter.
                square_number - the square number to advance to upon entering or None
            Return:
                CommandResult
            If square_number is None, then a roll is executed.
            
        """
        player = self.game_state.current_player
        if occupation_name in self._careersGame.occupation_names:
            occupation_entrance_square = self._careersGame.get_occupation_entrance_squares()[occupation_name]    # BorderSquare instance
            if self.can_enter(occupation_entrance_square,  occupation_name, player):
                
                player.board_location.border_square_number = occupation_entrance_square.number
                player.board_location.border_square_name=occupation_entrance_square.name
                player.board_location.occupation_name=occupation_name
                
                if square_number is None:
                    result = self.roll(1)
                else:
                    player.board_location.occupation_square_number=square_number
                    
                # execute the contents of the occupation square
                board_location = player.board_location
                result = self.execute_game_square(player, board_location)
                
                if result.return_code == CommandResult.ERROR:
                    return result
                else:   # successful occupation entry
                    res = self.where("am","I")
                    return CommandResult(result.return_code, f'{result.message}\n{res.message}', True)
            else:
                return CommandResult(CommandResult.ERROR, "Sorry, you don't meet the occupations entry conditions.", False)
        else:
            return CommandResult(CommandResult.ERROR, "No such occupation", False)
    
    def status(self):
        player = self.game_state.current_player
        message = player.player_info(include_successFormula=True)
        result = CommandResult(CommandResult.SUCCESS,  message, False)
        return result       
    
    def done(self):
        """End my turn and go to the next player
        """
        player = self.game_state.current_player
        player.opportunity_card = None
        player.experience_card = None
        result = CommandResult(CommandResult.SUCCESS,  "Turn is complete" , True)
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
            result = CommandResult(CommandResult.TERMINATE, f'Game is complete and saved to file: {sg_result.message}', True)
        else:
            result = CommandResult(CommandResult.TERMINATE, "Game is complete" , True)

        return result
    
    def quit(self, initials):
        """A single player, identified by initials, leaves the game.
        """
        result = CommandResult(CommandResult.SUCCESS, "'quit' command not yet implemented", False)
        return result
    
    def save(self):
        """Save the current game state
        """
        return self.save_game()
    
    def where(self, t1:str="am", t2:str="I"):
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
    
    def retire(self):
        """Retire this player to the retirement corner square (Spring Break, Holiday)
        
        """
        result = CommandResult(CommandResult.SUCCESS, "'retire' command not yet implemented", False)
        return result
    
    def bump(self, who=None):
        """The current player bumps another player occupying the same board square to Unemployment
            Note that it is possible to land on a square occupied by more than one player,
            for example if a player chooses NOT to bump that square will have 2 players.
            In that case the initials of the player to be bumped must be provided.
        
        """
        result = CommandResult(CommandResult.SUCCESS, "'bump' command not yet implemented", False)
        return result
    
    def bankrupt(self):
        """The current player declares bankruptcy.
            A bankrupt player looses all cash, experience and opportunity cards and essentially
            restarts the game with configured starting cash and salary, and positioned at the "Payday" square (border square 0).
            The player does retain occupation experience however including any and all college degrees.
        
        """
        result = CommandResult(CommandResult.SUCCESS, "'bankrupt' command not yet implemented", False)
        return result
    
    def list(self, what) ->str:
        """List the Experience or Opportunity cards held by the current player
            Arguments: what - 'experience' or 'opportunity'
            Returns: CommandResult.message is the stringified list of str(card).
                For Opportunity cards this is the text property.
                For Experience cards this is the number of spaces (if type is fixed), otherwise the type.
            
        """
        my_cards = []
        message = ""
        player = self.game_state.current_player
        if what is not None:
            if what.lower()=='opportunity':
                my_cards = player.my_opportunity_cards
            elif what.lower()=='experience':
                my_cards = player.my_experience_cards
        for card in my_cards:
            message += str(card) + "\n"
            
        result = CommandResult(CommandResult.SUCCESS, message, False)
        return result    

    def saved(self):
        """List the saved games, if any
        
        """
        result = CommandResult(CommandResult.SUCCESS, "'saved' command not yet implemented", False)
        return result    

    def load(self, gameid):
        """Load a previously saved game, identified by the game Id
        
        """
        result = CommandResult(CommandResult.SUCCESS, "'load' command not yet implemented", False)
        return result    

    def who(self, t1:str="am", t2:str="I"):
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
    
    def add(self, name, initials, stars=0, hearts=0, cash=0):
        """Add a player to the Game.
        """
        sf = SuccessFormula(stars=stars, hearts=hearts, cash=cash)
        player = Player(name=name, initials=initials)
        player.success_formula = sf
        player.salary = self._careersGame.game_parameters['starting_salary']
        player.cash = self._careersGame.game_parameters['starting_cash']
        self._careersGame.add_player(player)        # adds to GameState
    
    #####################################
    #
    # Game engine action implementations
    #
    #####################################
    
    def save_game(self):
        jstr = f'{{\n  "game_id" : "{self.gameId}",\n'
        jstr += f'  "gameState" : '
        jstr += self.game_state.to_JSON()
        jstr += "}\n"
        
        self.log(jstr)
        filename = self._logfile_path + "/" + self.gameId + "_saved.json"
        with open(filename, "w") as fp:
            fp.write(jstr)
        fp.close()
        self.log(f'game saved to {filename}')
        return CommandResult(CommandResult.SUCCESS, filename, True)

    def can_enter(self, occupation_entrance_square:BorderSquare, occupation_name, player:Player):
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
    
        
    def execute_card(self, player:Player, experienceCard:ExperienceCard=None, opportunityCard:OpportunityCard=None, spaces=0) -> CommandResult:
        """Execute the actions associated with this Experience card or Opportunity card
            Experience execution needs to handle the three types of wild cards.
            Returns: CommandResult
        """
        if experienceCard is not None:
            player.experience_card = experienceCard
            nspaces = experienceCard.spaces
            if experienceCard.spaces == 0 and experienceCard.type != 'fixed':    # must be a wild card
                nspaces = spaces

            message = f'{player.initials} Moving: {nspaces} spaces'
            self.log(message)
        elif opportunityCard is not None:
            player.opportunity_card = opportunityCard
            message = f'{player.initials} Playing: {opportunityCard.text}'
            #
            # Now execute this Opportunity card
            #
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
        
    def _execute_occupation_square(self, player:Player, game_square:OccupationSquare, board_location:BoardLocation):
        message = f'execute_occupation_square {board_location.occupation_name}  {board_location.occupation_square_number} for {player.player_initials}'
        self.log(message)
        
        return CommandResult(CommandResult.SUCCESS, message, False)
    
    def _execute_border_square(self, player:Player, game_square:BorderSquare, board_location:BoardLocation):
        message = f'execute_border_square {game_square.name}  {board_location.border_square_number} for {player.player_initials}'
        self.log(message)
        
        return CommandResult(CommandResult.SUCCESS, message, False)
    
    
    def exit_occupation(self, player, board_location:BoardLocation):
        """Applies exiting an occupation rules when a player exits an occupation path.
            Exiting can be done by rolling out, using an Experience, or using an Opportunity to go somewhere else.
            The occupation could be College ("occupationClass" : "college") or a regular Occupation ("occupationClass" : "occupation")
            * if the player entered the Occupation via Opportunity card, that card is removed from the player's hand
            * if the player completed the Occupation, credit is applied to the player's occupation record and up to 3 Experience cards given
            *
        """
        # TODO
        message = f'{player.initials} Leaving {board_location.occupation_name}'
        self.log(message)
        result = CommandResult(CommandResult.SUCCESS, message, True)
        return result
    
    def pass_payday(self, player, board_location:BoardLocation):
        """Performs any actions associated with landing on or passing the Payday square.
            Count laps (which may or may not be used) and dole out appropriate salary.
            Arguments:
                player - current Player reference
                board_location - the player's current BoardLocation
            The player's board location reflects the new position which will have a border_square_number >= 0.
        """
        salary = player.salary
        if board_location.border_square_number == 0:
            salary += salary
        player.cash += salary
        player.laps += 1
        message =  f'{player.initials} Collects {salary} salary'
        self.log(message)
        return CommandResult(CommandResult.SUCCESS, message, False)
        
        
        