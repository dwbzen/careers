'''
Created on Aug 5, 2022

@author: don_bacon
'''
from game.successFormula import SuccessFormula
from game.careersObject import CareersObject
from game.boardLocation import BoardLocation
from game.opportunityCard import OpportunityCard, OpportunityType, OpportunityActionType
from game.experienceCard import ExperienceCard
from game.gameConstants import PendingActionType
from game.pendingAction import PendingAction
from game.pendingActions import PendingActions
from game.gameConstants import GameType, PlayerType
from game.turnHistory import TurnHistory
from datetime import datetime
from typing import Dict, List, Union
import json

class Player(CareersObject):
    
    SPECIAL_PROCESSING = Dict[str, Union[str, List[int], int, float, Dict[str, int]]]
    
    def __init__(self, number=0, name="Player", player_id="", email="", salary=2000, cash=2000, initials="XXX", playerType:PlayerType=PlayerType.HUMAN):
        self._player_name = name
        self._player_initials = initials            # unique initials - no player can have the same initials
        self._salary_history = [salary]             # List[int] of salaries the player has attained
        self._starting_cash = cash
        self._starting_salary = salary
        self._cash = cash
        self._salary = salary
        self._success_formula = None         # my SuccessFormula
        self._player_id = player_id
        self._player_email = email
        self._player_type = playerType
        
        self._number = number               # my player number, values 0 to #players-1
        self._laps = 0                      # the number of times player has passed or landed on Payday
        # dict where key is the degree program and the values the number of degrees attained
        # when number of degrees in any program >= 4, the can_retire flag is automatically set
        self._my_degrees = dict()
        
        self._initialize()    # initialize starting parameters
        
        # dict where key is occupation name, value is the number of completed trips
        # when completed trips >= 3, the can_retire flag is automatically set
        self._occupation_record = {}   # Dict[str, int]:
        
        # player loan obligations are indexed by player_number: loans[player_number] = <loan amount>
        self._loans = {}    # Dict[int, int]:
        
        self._command_history:List[str] = []    # a list of commands executed by a player
        self._turn_history:TurnHistory = None   # turn command(s) and outcomes
        
        # minutes remaining in a timed game
        # this must be set externally as Player does not have access to gameState
        # 
        self.time_remaining = -1
        
        #
        # a player todo List are occupations and/or degrees the player must complete successfully
        # in addition to fulfilling their success formula
        #
        self._my_todos = {}    # filled in by applicable active plug-in(s)
        
    def _initialize(self):
        """Sets the starting values for all properties reset under bankruptcy rules.
        """
        
        self._set_starting_board_location() # always start on Payday corner square
        self._can_retire = False
        self._is_insured = False
        self._is_unemployed = False         # True when player lands on (or is sent to) Unemployment
        self._is_sick = False               # True when player lands on Hospital
        self._on_holiday = False            # True when the player lands on Holiday/Spring Break
        self._lose_turn = False             # If True the player loses their next turn. This is automatically reset when the turn is skipped.
        self._extra_turn = 0                # If >0 the player gets that number of additional turns. This is automatically decremented after that turn is taken.
        self._can_roll = False              # If True the player can roll or play an Experience card
        self._can_use_opportunity = True    # If True the play may use an Opportunity Card
        self._opportunity_card = None       # the OpportunityCard instance of the card last played, or None otherwise
        self._experience_card = None        # the ExperienceCard instance of the card currently in play, or None otherwise

        self._can_bump:List[str] = []       # initials of the players I can currently Bump
        
        # if a player has landed on an action_square, there is a pending action  which is the square's specialProcessing processing_type
        # there are currently 5: buy_hearts, buy_experience, buy_insurance, gamble, and cash_loss_or_unemployment
        # Also 'bankrupt' is a pending action that is set if the cash < 0
        #
        self._pending_actions = PendingActions()
        self._my_experience_cards = []       # list of ExperienceCards this player holds
        self._my_opportunity_cards = []      # list of OpportunityCards this player holds
        self._happiness = [0]                # record of happiness (hearts) earned. Cumulative amounts, total is happiness[-1]
        self._fame = [0]                     # record of fame (stars) earned. Cumulative amounts, total is fame[-1]
        self._savings = 0                    # savings account - populated with "pay", draw funds with "withdraw"
        self._point_losses = {"cash":5000,"hearts":10,"stars":10, "salary":2000}    # most recent point losses if any. Used by "use_insurance" command
        self._game_type = GameType.POINTS    # defaults to POINTS, can set to TIMED
    
    def set_starting_parameters(self, cash=2000, salary=2000):
        self._starting_cash = cash
        self._starting_salary = salary
        self._cash = cash
        self._salary = salary     
    
    def has_success(self) -> bool:
        return self.happiness >= self.success_formula.hearts and \
            self.fame >= self.success_formula.stars and \
            (self.cash + self.savings) >= self.success_formula.money
    
    @property
    def player_id(self):
        return self._player_id

    @player_id.setter
    def player_id(self, value):
        self._player_id = value

    @property
    def player_email(self) ->str:
        return self._player_email

    @player_email.setter
    def player_email(self, value:str):
        self._player_email = value

    @property
    def player_name(self):
        """Get the player's name."""
        return self._player_name
    
    @player_name.setter
    def player_name(self, value):
        self._player_name = value
        
    @property
    def player_initials(self) ->str:
        return self._player_initials
    
    @player_initials.setter
    def player_initials(self, value:str):
        self._player_initials = value
    
    @property
    def salary(self):
        return self._salary
    
    @salary.setter
    def salary(self, newSalary:int):
        if self._salary != newSalary:
            # print(f'*** {self._player_initials}  old salary: {self._salary}  newSalary: {newSalary} ***')
            self._salary = newSalary
            self._salary_history.append(newSalary)
        
    @property
    def salary_history(self) ->List[int]:
        return self._salary_history
    
    @property
    def cash(self):
        return self._cash
    
    @cash.setter
    def cash(self, value):
        self._cash = value
        if value < 0:
            self.add_pending_action(PendingActionType.BANKRUPT)
    
    @property
    def success_formula(self) -> SuccessFormula:
        return self._success_formula
    
    @success_formula.setter
    def success_formula(self, value:SuccessFormula):
        self._success_formula = value
        
    @property
    def number(self):
        return self._number
    
    @number.setter
    def number(self, value):
        self._number = value
        
    @property
    def my_degrees(self) ->Dict:
        return self._my_degrees
    
    @property
    def occupation_record(self) -> Dict[str, int]:
        return self._occupation_record
    
    @property
    def can_retire(self):
        return self._can_retire
    
    @can_retire.setter
    def can_retire(self, value:bool):
        self._can_retire = value
    
    @property
    def is_insured(self):
        return self._is_insured
    
    @is_insured.setter
    def is_insured(self, value:bool):
        self._is_insured = value
        
    @property
    def happiness(self):
        return self._happiness[-1]
    
    @happiness.setter
    def happiness(self, qty):
        self._happiness = [qty]
    
    @property   
    def fame(self):
        return self._fame[-1]
    
    @fame.setter
    def fame(self, qty):
        self._fame = [qty]
        
    @property
    def time_remaining(self)->int:
        return self._time_remaining
    
    @time_remaining.setter
    def time_remaining(self, value):
        self._time_remaining = value
    
    @property
    def board_location(self) -> BoardLocation:
        return self._board_location
    
    @board_location.setter
    def board_location(self, value:BoardLocation):
        self._board_location = value

    @property
    def my_todos(self) ->Dict:
        return self._my_todos
    
    @my_todos.setter
    def my_todos(self, value):
        self._my_todos = value

    def current_border_square_number(self):
        return self.board_location.border_square_number
        
    def current_border_square_name(self):
        return self.board_location.border_square_name

    def current_occupation_name(self):
        return self.board_location.occupation_name
    
    def current_occupation_square_number(self):
        return self.board_location.occupation_square_number
    
    def get_location(self, format="json") -> str:
        """Encapsulates the player's board location as a JSON-formatted string or dictionary depending on the format specified.
            Arguments:
                format - output format: "dict" for dictionary, "json" for JSON (the default)
            Returns: the border and occupation name and square number as a JSON string
                for example, 
                {"border": {"FMC": 4}, "occupation": {"FMC": 2}} - player is on square 2 of FMC (border square #4)
                {"border": {"Opportunity": 8}, "occupation": {"None": 0}}   - player is on border square 8
        """
        pdict_border =  {self.current_border_square_name():self.current_border_square_number()}
        occupation_name = "None" if self.current_occupation_name() is None else self.current_occupation_name()
        pdict_occupation = {occupation_name:0} if occupation_name=="None" else {occupation_name:self.current_occupation_square_number()}
        pdict = {"border":pdict_border, "occupation":pdict_occupation}
        if format == "dict":
            return pdict
        else:
            return json.dumps(pdict)
    
    @property
    def my_opportunity_cards(self) -> List[OpportunityCard]:
        return self._my_opportunity_cards
    
    @property
    def opportunity_card(self) -> OpportunityCard:
        """Returns the OpportunityCard currently in play, or None if no card is in play
        """
        return self._opportunity_card
    
    @opportunity_card.setter
    def opportunity_card(self, value:OpportunityCard):
        """Sets the OpportunityCard currently in play. After use, set to None.
        """
        self._opportunity_card = value
        
    def add_opportunity_card(self, thecard:OpportunityCard|List[OpportunityCard]):
        """Add a single OpportunityCard OR a List[OpportunityCard] to my deck
        """
        if isinstance(thecard, OpportunityCard):
            self._my_opportunity_cards.append(thecard)
        else:
            self._my_opportunity_cards += thecard
    
    @property
    def my_experience_cards(self) -> List[ExperienceCard]:
        return self._my_experience_cards
        
    @property
    def experience_card(self) -> ExperienceCard:
        """Returns the ExperienceCard currently in play, or None if no card is in play
        """
        return self._experience_card
    
    @experience_card.setter
    def experience_card(self, value:ExperienceCard):
        """Sets the ExperienceCard currently in play
        """
        self._experience_card = value
        
    def add_experience_card(self, thecard:ExperienceCard|List[ExperienceCard]):
        """Add a single ExperienceCard OR a List[ExperienceCard] to my deck
        """
        if isinstance(thecard, ExperienceCard):
            self._my_experience_cards.append(thecard)
        else:
            self._my_experience_cards += thecard
    
    @property
    def is_unemployed(self):
        return self._is_unemployed
    
    @is_unemployed.setter
    def is_unemployed(self, value):
        self._is_unemployed = value
    
    @property
    def is_sick(self):
        return self._is_sick
    
    @is_sick.setter
    def is_sick(self, value):
        self._is_sick = value
        
    @property
    def on_holiday(self):
        return self._on_holiday
    
    @on_holiday.setter
    def on_holiday(self, value):
        self._on_holiday = value
        
    @property
    def lose_turn(self):
        return self._lose_turn
    
    @lose_turn.setter
    def lose_turn(self, value):
        self._lose_turn = value
     
    @property   
    def extra_turn(self):
        return self._extra_turn
    
    @extra_turn.setter
    def extra_turn(self, value):
        self._extra_turn = value
        
    @property
    def laps(self):
        return self._laps
    
    @laps.setter
    def laps(self, value):
        self._laps = value
    
    @property
    def loans(self) -> Dict[int, int]:
        return self._loans
    
    @property
    def can_bump(self) -> List[str]:
        return self._can_bump       #a list of Player
    
    @can_bump.setter
    def can_bump(self, other_players:List[str]):
        self._can_bump = other_players    #a list of Player
        
    @property
    def can_roll(self):
        return self._can_roll
    
    @can_roll.setter
    def can_roll(self, value):
        self._can_roll = value
        
    @property
    def can_use_opportunity(self):
        return self._can_use_opportunity
    
    @can_use_opportunity.setter
    def can_use_opportunity(self, value):
        self._can_use_opportunity = value
        
    @property
    def savings(self) ->int:
        return self._savings
    
    @savings.setter
    def savings(self, value:int):
        self._savings = value
        
    def add_savings(self, amount:int):
        self._savings = self._savings + amount
        
    def withdraw(self, amount:int) ->int:
        amt = amount if amount <= self.savings else self.savings
        return amt
    
    @property
    def point_losses(self) -> dict:
        return self._point_losses
    
    def add_point_loss(self, key:str, value:int):
        self._point_losses[key] = value
    
    def clear_point_losses(self):
        self.point_losses["cash"] = 0
        self.point_losses["hearts"] = 0
        self.point_losses["stars"] = 0
        self.point_losses["salary"] = 0
        
    @property
    def game_type(self)->GameType:
        return self._game_type
    
    @game_type.setter
    def game_type(self, value:GameType):
        self._game_type = value
        
    @property
    def player_type(self) ->PlayerType:
        return self._player_type
    
    @player_type.setter
    def player_type(self, value:PlayerType):
        self._player_type = value
    
    @property
    def turn_history(self) ->TurnHistory:
        return self._turn_history
    
    @turn_history.setter
    def turn_history(self, value):
        self._turn_history = value

    def add_command(self, command:str):
        """Adds a command to the player's command_history and current Turn
        """
        self._command_history.append(command)
        
        if self.turn_history is not None:
            turn = self.turn_history.get_turn()
            turn.commands.append(command)
    
    def get_command(self, index:int=-1) ->str:
        return self._command_history[index]
        
    def add_pending_action(self, action:PendingActionType, game_square_name:str=None, amount:SPECIAL_PROCESSING=None, dice:int | List[int]=0):
        self._pending_actions.add(PendingAction(action, game_square_name, amount, dice))
        
    def get_pending_action(self, index=-1) -> PendingAction:
        """Gets the PendingAction at the requested index
            Arguments:
                index = the index of the PendingAction, defaults to -1 which returns the last (most recently added) PendingAction
            Returns:
                PendingAction, also it is NOT removed from the player's  PendingActions
        """
        pa = self._pending_actions.get(index, remove=False)
        return pa
    
    def has_pending_action(self, pending_action_type:PendingActionType) -> bool:
        """Determine if the player has a PendingAction of a given PendingActionType
            Returns: True is so, False otherwise
        """
        return self._pending_actions.index_of(pending_action_type) >= 0
        
    def clear_pending(self,  pending_action_type:PendingActionType=None):
        """Clear all the PendingActions except for pending_action_type
            Arguments:
                pending_action_type: the PendingActionType not to clear, default is None
                                     which would result in clearing all pending actions
            Note this also sets the player's onHoliday flag to False
        """
        self.clear_pending_actions(pending_action_type)
        self._on_holiday = False

    def clear_pending_actions(self, pending_action_type:PendingActionType=None):
        """Removes all PendingAction except a given PendingActionType from the player's PendingActions
            If pending_action_type is None, all pending actions are removed.
        """
                
        if self._pending_actions.size() > 0:
            self._pending_actions.remove_all_but(pending_action_type)
                    
    @property
    def pending_actions(self) -> PendingActions:
        return self._pending_actions
    
    def pending_actions_size(self):
        return self._pending_actions.size()

    def find_pending_action(self, pendingActionType:PendingActionType) -> PendingAction|None:
        return self._pending_actions.find(pendingActionType)
    
    def has_pending_actions(self) -> bool:
        return self.pending_actions_size() > 0
    
    def _get_pending(self) ->dict:
        return self._pending_actions.to_dict()
    
    def get_total_loans(self):
        total = 0
        for v in self._loans.values():
            total += v
        return total
    
    def add_loan(self, amt:int, player_number:int):
        if player_number in self._loans:
            self._loans[player_number] = self._loans[player_number] + amt
        else:
            self._loans[player_number] = amt
    
    def get_opportunity_cards(self) -> List[OpportunityCard]:
        """Returns a of dict of Opportunity cards indexed by number
            This method used to display the cards to a player for selection.
            Return format is:
            {  4 :  { "quantity" : 3,  "text" : "card text", "card" : <card instance>} }
        """
        cards_dict = {}
        for card in self.my_opportunity_cards:
            key = card.number
            if key in cards_dict:
                cd = cards_dict[key]
                cd["quantity"] = cd["quantity"] + 1
            else:
                cards_dict[key] = {"quantity" : 1, "text" : card.text, "card" : card}
        return cards_dict
    
    def get_experience_cards(self):
        """Returns a of dict of Experience cards indexed by number.
            This method used to display the cards to a player for selection.
            Return format is:
            {  4 :  { "quantity" : 3,  "spaces" : "4", "card" : <card instance>} } if spaces > 0,  or "spaces" : <card type>
        """        
        cards_dict = {}
        for card in self.my_experience_cards:
            key = card.number
            if key in cards_dict:
                cd = cards_dict[key]
                cd["quantity"] = cd["quantity"] + 1
            else:
                spaces = card.spaces
                if spaces > 0:
                    cards_dict[key] = {"quantity" : 1, "spaces" : str(spaces), "card" : card}
                else:
                    cards_dict[key] = {"quantity" : 1, "spaces" : card.card_type, "card" : card}
        return cards_dict
    
    def used_opportunity(self):
        """The player has used the saved Opportunity card, remove from their deck
        """
        if self.opportunity_card is not None:
            self.remove_opportunity_card(self._opportunity_card)
    
    def remove_opportunity_card(self, card:OpportunityCard):
        self.my_opportunity_cards.remove(card)
    
    def used_experience(self):
        """The player has used the saved Experience card. Set it to None and remove from their deck
        """
        if self.experience_card is not None:
            self.remove_experience_card(self.experience_card)
            self._experience_card = None
    
    def remove_experience_card(self, card:ExperienceCard):
            self.my_experience_cards.remove(card)
                
    def add_degree(self, degree_program:str):
        if degree_program in self.my_degrees:
            count = self.my_degrees[degree_program]
            # max of 4 degrees in any degree program
            count += 1
            if count <= 4:
                self._my_degrees[degree_program] = count
            if count >= 4:
                self.can_retire = True
        else:
            self._my_degrees[degree_program] = 1
    
    def add_occupation(self, occupation_name:str):
        if occupation_name in self.occupation_record:
            count = self._occupation_record[occupation_name] + 1
            self._occupation_record[occupation_name] = count
            if count >= 3:
                self.can_retire = True
        else:
            self._occupation_record[occupation_name] = 1
            
        
    def add_hearts(self, nhearts:int):
        """Adds the number of Hearts indicated. Could be negative if losing hearts.
            If so, the resulting number will never be < 0.
        """
        if nhearts < 0:    # subtract this amount but don't go below 0
            if self.happiness + nhearts < 0:
                nhearts = -self.happiness
        self._happiness.append(self.happiness + nhearts)
    
    def add_stars(self, nstars:int):
        if nstars < 0:    # subract this amount but don't go below 0
            if self.fame + nstars < 0:
                nstars = -self.fame
        self._fame.append(self.fame + nstars)
        
    def add_points(self, what:str, qty:int):
        '''Add hearts, stars or cash
        '''
        if 'hearts' in what:
            self.add_hearts(qty)
        elif 'stars' in what:
            self.add_stars(qty)
        elif 'cash' in what:
            self.add_cash(qty)
        else:
            raise AttributeError(f'{what} is not a valid choice')
        
    def add_cash(self, money:int):
        """Adds cash to the players cash-on-hand.
            This can be negative if losing cash.
            If the cash falls below 0, the 'bankrupt' pending_action is set.
        """
        self.cash = self.cash + money
        if self._cash < 0:
            self.pending_action = 'bankrupt'
    
    def add_to_salary(self, money:int): #  again, could be negative amount
        self.salary = self.salary + money
        self._salary_history.append(self.salary)
        
    def total_points(self):
        return self.happiness  + self.fame + self.cash_points() - self.loan_points() 
    
    def cash_points(self):
        """Cash points is the amount of cash/1000
        """
        return self.cash // 1000
    
    def loan_points(self):
        return self.get_total_loans() // 1000
    
    def net_worth(self):
        '''Net worth is the cash + savings - loans
        '''
        return self.savings + self.cash - self.get_total_loans()
    
    def is_complete(self):
        """Returns True if this players has met or surpassed each success formula item:
            happiness (hearts), fame (stars), money, False otherwise
            In a timed game, this returns True if time_remaining <= 0
            Note the result is only valid if the game has started (game_state.started is True)
    
        """
        if self.game_type is GameType.POINTS:
            complete = self.happiness >= self.success_formula.hearts and \
                       self.fame >= self.success_formula.stars and \
                       self.cash_points() >= self.success_formula.money
        else:
            complete = self.time_remaining <= 0
                       
        return complete

    def save(self, gameId:str|None=None):
        """Persist this player's state to a JSON file.
        File name is "player_" + player_initials + yyyy-mm-dd_hhmmss + _state.json"
        
        """
        today = datetime.now()
        fdate = '{0:d}-{1:02d}-{2:02d}_{3:02d}{4:02d}{5:02d}'.format(today.year,today.month, today.day, today.hour, today.minute, today.second)
        if gameId is None:
            filename = f'player_{self._player_initials}_{fdate}_state.json '
        else:
            filename = f'{gameId}_player_{self._player_initials}_{fdate}_state.json'
        #
        # save in jsonpickle format
        #
        jstr = self.json_pickle()
        with open(filename, "w") as fp:
            fp.write(jstr)
        fp.close()        
        return filename
    
    def bankrupt_me(self):
        """Force this Player into bankruptcy.
            A bankrupt player looses all Fame and Happiness points and all cash except the starting amount (typically $2000).
            Also the player turns in all Experience and Opportunity cards
            and his/her/they board position set to Payday (square 0).
            The player does however retain work history and any degrees earned. Retirement privileges, if any, are revoked.
            A player can earn retirement privileges back by fulfilling the criteria a second time, presumably with
            different/new occupations and/or degree program.
            A player may declare bankruptcy at any time.
            If the player's cash-on-hand is < 0 at the start of their turn, the player
            is forced into bankruptcy automatically.
            
        """
        self.cash = self._starting_cash
        self.salary = self._starting_salary
        self._salary_history = [self.salary]
        self._initialize()
    
    def player_info(self, include_successFormula:bool=False, outputFormat:str='text', include_degrees=True, \
                    include_board_location=True, include_card_values=True) ->str:
        '''Returns key player information in the desired format.
            Arguments:
                include_successFormula - if True, include the player's success formula. Default is False
                include_degrees - if True, include the player's degrees (if any). Default is True
                include_board_location - if True, include the player's current BoardLocation. Default is True.
                outputFormat - 'json', 'dict' or 'text'. Default is 'text'
                include_card_values - include the numeric value of each Opportunity and Experience card. Default is True.
            
            Card values are assigned by card_type and are in the cards JSON files under "types".
        '''
        v = self.get_total_loans()
        net_worth = self.net_worth()
        progress =  {"cash":self.cash, "stars":self.fame, "hearts":self.happiness, "points":self.total_points()}
        info_dict = {"player":self.player_initials,  "salary":self.salary, 'progress' : progress }
        info_dict.update( {"insured":self.is_insured, "unemployed":self.is_unemployed, "sick":self.is_sick, \
                           "extra_turn":self.extra_turn, "can_retire":self.can_retire, "net_worth":net_worth} )
        info_dict.update( self._get_pending() )
        
        if self.pending_actions.size() == 0:
            pending_string = "Pending actions: None"  
        else:
            pending_string = "Pending actions: {"
            for pa in self.pending_actions.get_all():
                pending_string +=  f'{pa.pending_action_type.value}, '
            pending_string = pending_string[:len(pending_string)-2] + "}"
          
        fstring = \
f'''Initials: {self.player_initials}: Salary:{self.salary}, Cash: {self.cash},  Fame: {self.fame}, Happiness: {self.happiness}, Points: {self.total_points()}
Insured: {self.is_insured}, Unemployed: {self.is_unemployed}, Sick: {self.is_sick}, Can Retire: {self.can_retire}, Net worth: {net_worth}
{pending_string}, Extra turn: {self.extra_turn} '''

        if self.cash < 0:
            fstring = f'{fstring}\nALERT: You have negative cash amount and must declare bankruptcy OR borrow the needed funds from another player!!'
            info_dict.update( {"is_bankrupt":True})
            
        if include_successFormula and self.game_type is GameType.POINTS:
            fstring = f'{fstring}\nSuccess Formula: {self.success_formula}'
            sf = {'success_formula' : self.success_formula.to_dict()}
            info_dict.update( sf)
            
        if include_degrees:
            list_dict = self.list("degrees", "condensed")
            degrees = json.dumps(list_dict)
            fstring = f'{fstring}\nDegrees: {degrees}'
            info_dict.update({'degrees' : list_dict})
            
        if include_board_location:
            board_locn = str(self.board_location)
            fstring = f'{fstring}\nBoardLocation: {board_locn}'
            info_dict.update( {"board_location" : self.board_location.to_dict()} )
            
        if include_card_values:
            #
            # sum the values of the player's Experience and Opportunity cards
            # return as a Dict having the count and the total value  {"count" : 2, "value" : 8} 
            # 
            opportunity_card_value = 0
            opportunity_card_count = 0
            experience_card_value = 0
            experience_card_count = 0
            for card in self.my_opportunity_cards:
                opportunity_card_count += 1
                opportunity_card_value += card.value
            for card in self.my_experience_cards:
                experience_card_count += 1
                experience_card_value += card.value
            
            cdict = {"opportunity" : {"count": opportunity_card_count, "value" : opportunity_card_value}}
            cdict.update({"experience" : {"count": experience_card_count, "value" : experience_card_value}})
            fstring = f'{fstring}\n{cdict}'
            info_dict.update(cdict)
            
        if self.game_type is GameType.TIMED:
            fstring = f'{fstring}\nGame Time Remaining: {self.time_remaining} minutes'
            info_dict.update({"time_remaining": self.time_remaining})
            
        if v > 0:
            fstring = f'{fstring}\nloans: {v}'
            info_dict.update( {"loans":self.loans})
        
        # add number of opportunity and experience cards
        nOpportunities = len(self._my_opportunity_cards)
        nExperiences = len(self._my_experience_cards)
        fstring = f'{fstring},\nopportunities:{nOpportunities}, experiences:{nExperiences}'
        info_dict.update( {"opportunities":nOpportunities, "experiences":nExperiences})
            
        outval = fstring
        if outputFormat=='json':
            outval = json.dumps(info_dict)
        elif outputFormat=='dict':
            outval = info_dict 
        return outval
    
    def get_current_location(self) -> BoardLocation:
        """Gets the location of this player on the board.
            Returns: current_board_location
        
        """
        return  self.current_board_location
    
    def has_opportunity(self, opportunity_card_type:OpportunityType,  opportunity_action_type:OpportunityActionType=None)->bool:
        """Check if this player has an opportunity card of a given OpportunityType and OpportunityActionType
            Arguments:
                opportunity_card_type - OpportunityType to search for
                opportunity_action_type - OpportunityActionType to search for, applies only when OpportunityType is ACTION
            Returns:
                True if the player has that opportunity card, else False
        """
        result = False
        for card in self.my_opportunity_cards:
            if card.opportunity_type is opportunity_card_type:
                if opportunity_action_type is None:
                    result = True
                else:
                    if card.action_type is not None and card.action_type is opportunity_action_type:
                        result = True
    
        return result
    
    def list(self, what:str, how:str) -> dict:
        """List the Experience or Opportunity cards held this player
            Arguments: 
                what - 'experience', 'opportunity', 'degrees'  or 'all'
                how - display control: 'full', 'condensed' or 'count'
            Returns: CommandResult.message is the stringified list of str(card).
                For Opportunity cards this is the text property.
                For Experience cards this is the number of spaces (if type is fixed), otherwise the type.
            
        """
        listall = (what.lower() == 'all')
        list_dict = {}
        #
        # list opportunity cards
        #
        if what.lower().startswith('opp') or listall:
            ncards = len(self.my_opportunity_cards)
            list_dict['number_opportunity_cards'] = ncards
            if ncards > 0:
                if how == 'full':
                    list_dict['opportunity_cards'] = [cd.to_dict() for cd in self.my_opportunity_cards]
                elif how.startswith('cond'):
                    list_dict['opportunity_cards'] = sorted([f'{cd.number:>2}: {cd.text}' for cd in self.my_opportunity_cards])
            else:
                list_dict["opportunity_cards"] = []
         
        #
        # list experience cards
        #           
        if what.lower().startswith('exp') or listall:
            ncards = len(self.my_experience_cards)
            list_dict['number_experience_cards'] = ncards
            if ncards > 0:
                if how == 'full':
                    list_dict['experience_cards'] = [cd.to_dict(include_range=False) for cd in self.my_experience_cards]
                elif how.startswith('cond'):
                    list_dict['experience_cards'] = sorted([f'{cd.number:>2}: {str(cd)}'  for cd in self.my_experience_cards])
            else:
                list_dict["experience_cards"] = []
                
        if what.lower().startswith('degree') or listall:    # list degrees completed
            ndegrees = len(self.my_degrees)
            list_dict['number_of_degrees'] = ndegrees
            if ndegrees > 0:
                list_dict['degrees'] = self.my_degrees
        
        if what.lower().startswith('occ') or listall: # list occupations completed
            noccupations = len(self.occupation_record)
            if noccupations > 0:
                list_dict['occupations_completed'] = noccupations
                list_dict['occupations'] = self.occupation_record
            else:
                list_dict["occupations"] = []
                list_dict["occupations_completed"] = []

        if what.lower().startswith('command') or listall: # command history
            list_dict["commands"] = self._command_history
        
        if what.lower().startswith('can_bump') or listall:  # list the players this player can bump, by initials
            list_dict["can_bump"] = self.can_bump

        return list_dict
    
    def _set_starting_board_location(self):
        self._board_location = BoardLocation(border_square_number=0, border_square_name="Payday", occupation_name=None, occupation_square_number=0 )
    
    def info(self):
        return  f' "name" : "{self.player_name}",  "number" : "{self.number}",  "initials" : "{self.player_initials}"'
    
    def __str__(self):
        fstring = f'Cash: {self.cash}  Fame: {self.fame}  Happiness: {self.happiness}'
        return f'{self.number}. {self.player_name} ({self.player_initials}) : salary:{self.salary}\n{fstring}\nSuccess Formula: {self.success_formula}'
    
    def to_dict(self):
        pdict = {"name" : self.player_name, "number" : self.number, "initials" : self.player_initials}
        pdict['success_formula'] = self._success_formula.to_dict()
        points = self.total_points()
        pdict['score'] = {"cash":self.cash, "fame":self.fame, "happiness":self.happiness, "total_points":points}
        pdict['loans'] = self.loans 
        pdict['board_location'] = self.board_location.to_dict()
        pdict['is_insured'] = self.is_insured
        pdict['is_sick'] = self.is_sick
        pdict['is_unemployed'] = self.is_unemployed
        pdict['can_roll'] = self.can_roll
        pdict['extra_turn'] = self.extra_turn
        pdict['can_use_opportunity'] = self.can_use_opportunity
        pdict['occupation_record'] = self.occupation_record
        pdict['_id'] = self.player_id
        pdict['email'] = self.player_email
        pdict["salary_history"] = self.salary_history
        pdict.update(self.list('all','condensed'))
        pdict.update(self._get_pending())
        
        return pdict

    def to_JSON(self):
        return json.dumps(self.to_dict(), indent=2)

    def _load(self, player_dict:dict):
        """Loads game state player info from a previously saved CareersGame
            TODO
        """
        self.player_name = player_dict["name"]
        self.number = player_dict["number"]
        self.player_initials = player_dict["initials"]
        self.player_id = player_dict["_id"]
        self.player_email = player_dict["email"]
        self.is_insured = player_dict["is_insured"]
        self.is_sick = player_dict["is_sick"]
        self.is_unemployed = player_dict["is_unemployed"]
        self.can_bump = player_dict.get("can_bump", False)
        self.extra_turn = player_dict["extra_turn"]
        self.can_roll = player_dict["can_roll"]
        self.can_use_opportunity = player_dict["can_use_opportunity"]
        success_formula = player_dict["success_formula"]
        self.success_formula = SuccessFormula(stars=success_formula["stars"], hearts=success_formula["hearts"], money=success_formula["money"])
        
        board_location = player_dict["board_location"]
        self.board_location = BoardLocation(board_location["border_square_number"], board_location["border_square_name"],
                                            board_location["occupation_name"], board_location["occupation_square_number"])
        
        occupations = player_dict["occupations"]    # Dict[str, int]:
        if len(occupations)>0:
            for occupation_name in occupations.keys():
                self._occupation_record[occupation_name] = occupations[occupation_name]
            
        command_history = player_dict["commands"]               # List[str]
        for command in command_history: self.add_command(command)
        
        score = player_dict["score"]                            # {"cash":self.cash, "fame":self.fame, "happiness":self.happiness, "total_points":points}
        self.cash = score["cash"]
        self.fame = score["fame"]
        self.happiness = score["happiness"]
        self.points = score["total_points"]
        
        salary_history = player_dict["salary_history"]          # List[int]
        for money in salary_history: self.salary = money
        
        pending_actions = player_dict["pending_actions"]        # List[PendingAction]  TODO
        for pa in pending_actions:
            pending_action_type = PendingActionType[pa["pending_action_type"].upper()]
            self.add_pending_action(pending_action_type, pa["pending_game_square_name"], pa["pending_amount"], pa["pending_dice"])

        print(f'player {self.player_initials} loaded')
    
if __name__ == '__main__':
    print(Player.__doc__)
    