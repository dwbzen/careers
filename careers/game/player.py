'''
Created on Aug 5, 2022

@author: don_bacon
'''
from game.successFormula import SuccessFormula
from game.careersObject import CareersObject
from game.boardLocation import BoardLocation
from game.opportunityCard import OpportunityCard
from game.experienceCard import ExperienceCard
from game.gameConstants import PendingAction
from datetime import datetime
from typing import Dict, List, Union
import json

class Player(CareersObject):
    
    SPECIAL_PROCESSING = Dict[str, Union[str, List[int], int, float, Dict[str, int]]]
    
    def __init__(self, number=0, name="Player", salary=2000, cash=2000, initials="XXX"):
        self._player_name = name
        self._player_initials = initials            # unique initials - no player can have the same initials
        self._salary_history = [salary]             # list of salaries the player has attained
        self.set_starting_parameters(cash, salary)
        self._success_formula = None         # my SuccessFormula
        
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
        self._opportunity_card = None       # the OpportunityCard instance of the card currently in play, or None otherwise
        self._experience_card = None        # the ExperienceCard instance of the card currently in play, or None otherwise

        self._can_bump = []                 # the players I can currently Bump
        
        # if a player has landed on an action_square, there is a pending action  which is the square's specialProcessing processing_type
        # there are currently 5: buy_hearts, buy_experience, buy_insurance, gamble, and cash_loss_or_unemployment
        # Also 'bankrupt' is a pending action that is set if the cash < 0
        #
        self._pending_action = None
        self._pending_amount = 0
        self._pending_game_square = None     # reference to the BorderSquare or OccupationSquare associated with this pending_action
        self._pending_dice = 0               # the number of dice to use or 0 if N/A
        self._my_experience_cards = []       # list of ExperienceCards this player holds
        self._my_opportunity_cards = []      # list of OpportunityCards this player holds
        self._happiness = [0]                # record of happiness (hearts) earned. Cumulative amounts, total is happiness[-1]
        self._fame = [0]                     # record of fame (stars) earned. Cumulative amounts, total is fame[-1]
        self._savings = 0                    # savings account - populated with "pay", draw funds with "withdraw"
    
    @property
    def player_name(self):
        """Get the player's name."""
        return self._player_name
    
    @player_name.setter
    def player_name(self, value):
        self._player_name = value
        
    @property
    def player_initials(self):
        return self._player_initials
    
    @property
    def salary(self):
        return self._salary
    
    @salary.setter
    def salary(self, newSalary):
        self._salary = newSalary
        self._salary_history.append(newSalary)
        
    @property
    def salary_history(self):
        return self._salary_history
    
    @property
    def cash(self):
        return self._cash
    
    @cash.setter
    def cash(self, value):
        self._cash = value
        if value < 0:
            self.pending_action = 'bankrupt'
    
    @property
    def success_formula(self):
        return self._success_formula
    
    @success_formula.setter
    def success_formula(self, value):
        self._success_formula = value
        
    @property
    def number(self):
        return self._number
    
    @number.setter
    def number(self, value):
        self._number = value
        
    @property
    def my_degrees(self):
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
    
    @property   
    def fame(self):
        return self._fame[-1]
    
    @property
    def board_location(self) -> BoardLocation:
        return self._board_location
    
    @board_location.setter
    def board_location(self, value:BoardLocation):
        self._board_location = value


    def current_border_square_number(self):
        return self.board_location.border_square_number
        
    def current_border_square_name(self):
        return self.board_location.border_square_name

    def current_occupation_name(self):
        return self.board_location.occupation_name
    
    def current_occupation_square_number(self):
        return self.board_location.occupation_square_number
    
    @property
    def my_opportunity_cards(self):
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
        
    def add_opportunity_card(self, thecard:OpportunityCard):
        """Add a single OpportunityCard to my deck
        """
        self._my_opportunity_cards.append(thecard)
    
    @property
    def my_experience_cards(self):
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
        
    def add_experience_card(self, thecard:ExperienceCard):
        """Add a single ExperienceCard to my deck
        """
        self._my_experience_cards.append(thecard)
    
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
    def can_bump(self):
        return self._can_bump       #a list of Player
    
    @can_bump.setter
    def can_bump(self, other_players):
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
    def pending_action(self) -> PendingAction:
        return self._pending_action
    
    @pending_action.setter
    def pending_action(self, value:PendingAction):
        self._pending_action = value
    
    @property  
    def pending_amount(self) -> SPECIAL_PROCESSING:
        return self._pending_amount
    
    @pending_amount.setter
    def pending_amount(self, value:SPECIAL_PROCESSING):
        self._pending_amount = value
        
    @property
    def pending_game_square(self):
        return self._pending_game_square    # a GameSquare reference
    
    @pending_game_square.setter
    def pending_game_square(self, value):
        self._pending_game_square = value
        
    @property
    def pending_dice(self) ->Union[int,List[int]]:
        return self._pending_dice
    
    @pending_dice.setter
    def pending_dice(self, value:Union[int,List[int]]):
        '''Set pending dice for the current pending_action.
            This can be an int to represent the number or spaces,
            or the actual dice roll as a List.
        '''
        self._pending_dice = value
    
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
        
    def set_pending(self, action:PendingAction, game_square=None, amount:SPECIAL_PROCESSING=None, dice:Union[int,List[int]]=0):
        self.pending_action = action
        self.pending_game_square = game_square
        self.pending_amount = amount
        self.pending_dice = dice
        
    def set_starting_parameters(self, cash:int, salary:int):
        self._starting_cash = cash
        self._starting_salary = salary
        self.cash = cash
        self.salary = salary
    
    def get_total_loans(self):
        total = 0
        for v in self._loans.values():
            total += v
        return total
    
    def add_loan(self, amt, player_number):
        if player_number in self._loans:
            self._loans[player_number] = self._loans[player_number] + amt
        else:
            self._loans[player_number] = amt
    
    def get_opportunity_cards(self) -> list:
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
        """The player has used the saved Opportunity card. Set it to None and remove from their deck
        """
        if self.opportunity_card is not None:
            self.my_opportunity_cards.remove(self._opportunity_card)
            self._opportunity_card = None
    
    def used_experience(self):
        """The player has used the saved Experience card. Set it to None and remove from their deck
        """
        if self.experience_card is not None:
            self.my_experience_cards.remove(self.experience_card)
            self._experience_card = None
                
    def add_degree(self, degree_program):
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
    
    def add_occupation(self, occupation_name):
        if occupation_name in self.occupation_record:
            count = self._occupation_record[occupation_name] + 1
            self._occupation_record[occupation_name] = count
            if count >= 3:
                self.can_retire = True
        else:
            self._occupation_record[occupation_name] = 1
            
        
    def add_hearts(self, nhearts):
        """Adds the number of Hearts indicated. Could be negative if losing hearts.
            If so, the resulting number will never be < 0.
        """
        if nhearts < 0:    # subract this amount but don't go below 0
            if self.happiness + nhearts < 0:
                nhearts = -self.happiness
        self._happiness.append(self.happiness + nhearts)
    
    def add_stars(self, nstars):
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
        
    def add_cash(self, money):
        """Adds cash to the players cash-on-hand.
            This can be negative if losing cash.
            If the cash falls below 0, the 'bankrupt' pending_action is set.
        """
        self.cash = self.cash + money
        if self._cash < 0:
            self.pending_action = 'bankrupt'
    
    def add_to_salary(self, money): #  again, could be negative amount
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
    
    def is_complete(self):
        """Returns True if this players's total points are >= game total points, False otherwise
    
        """
        return  self.total_points() >= self.success_formula.total_points()

    def save(self, gameId=None):
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
    
    def player_info(self, include_successFormula=False):
        v = self.get_total_loans()
        pending_action = self.pending_action.value if self.pending_action is not None else "None"
        fstring = f'''salary:{self.salary}, Cash: {self.cash},  Fame: {self.fame}, Happiness: {self.happiness}, 
Insured: {self.is_insured}, Unemployed: {self.is_unemployed}, Sick: {self.is_sick}, 
Pending action: {pending_action}, Pending amount: {self.pending_amount} Pending dice: {self.pending_dice} '''

        if self.cash < 0:
            fstring = f'{fstring}\nALERT: You have negative cash amount and must declare bankruptcy OR borrow the needed funds from another player!!'
        if include_successFormula:
            fstring = f'{fstring}\nSuccess Formula: {self.success_formula}'
        if v > 0:
            fstring = f'{fstring}\nloans: {v}'
        return fstring
    
    def get_current_location(self) -> BoardLocation:
        """Gets the location of this player on the board.
            Returns: current_board_location
        
        """
        return  self.current_board_location
    
    def _set_starting_board_location(self):
        self._board_location = BoardLocation(border_square_number=0, border_square_name="Payday", occupation_name=None, occupation_square_number=0 )
        
    def clear_pending(self):
        self._pending_action = None
        self._pending_amount = 0
        self._pending_game_square = None
        self._pending_dice = 0
        self._on_holiday = False
    
    def info(self):
        return  f' "name" : "{self.player_name}",  "number" : "{self.number}",  "initials" : "{self.player_initials}"'
    
    def __str__(self):
        fstring = f'Cash: {self.cash}  Fame: {self.fame}  Happiness: {self.happiness}'
        return f'{self.number}. {self.player_name} ({self.player_initials}) : salary:{self.salary}\n{fstring}\nSuccess Formula: {self.success_formula}'
    
    def to_dict(self):
        pdict = {"name" : self.player_name, "number" : self.number, "initials" : self.player_initials}
        pdict['successFormula'] = self._success_formula.to_dict()
        points = self.total_points()
        pdict['score'] = {"cash":self.cash, "fame":self.fame, "happiness":self.happiness, "total_points":points, "is_insured":self.is_insured}
        pdict['loans'] = self.loans
        pdict['board_location'] = self.board_location.to_dict()
        pdict['is_sick'] = self.is_sick
        pdict['is_unemployed'] = self.is_unemployed
        pdict['can_roll'] = self.can_roll
        pdict['can_use_opportunity'] = self.can_use_opportunity
        pdict['occupation_record'] = self.occupation_record
        
        return pdict

    def to_JSON(self):
        return json.dumps(self.to_dict(), indent=2)

    
if __name__ == '__main__':
    player = Player(0, name='Don', initials='DWB')
    sf = SuccessFormula(stars=40, hearts=10, cash=50)
    player.success_formula = sf

    
    print(str(player))
    print(repr(player))
    
    player.add_cash(5000)
    player.add_hearts(3)
    player.add_stars(6)
    print("\n" + player.player_info(include_successFormula=False) )
    player.add_to_salary(2000)
    print("\n" + player.player_info(include_successFormula=True)  )
    
    print("\njson_pickle:")
    print(player.json_pickle())
    print("\nto_JSON:")
    print(player.to_JSON())
    