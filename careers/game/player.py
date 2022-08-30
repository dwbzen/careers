'''
Created on Aug 5, 2022

@author: don_bacon
'''
from game.successFormula import SuccessFormula
from game.careersObject import CareersObject
from game.boardLocation import BoardLocation
from game.opportunityCard import OpportunityCard
from game.experienceCard import ExperienceCard

from datetime import datetime

class Player(CareersObject):
    
    def __init__(self, number=0, name="Player", salary=2000, cash=2000, initials="XXX"):
        self._player_name = name
        self._player_initials = initials            # unique initials
        self._salary_history = []                   # list of salaries the player has attained
        self._salary = salary                       # my current salary
        self._cash = cash                           # cash on hand
        self._success_formula = None         # my SuccessFormula
        self._happiness = [0]                # record of happiness (hearts) earned. Cumulative amounts, total is happiness[-1]
        self._fame = [0]                     # record of fame (stars) earned. Cumulative amounts, total is fame[-1]
        
        self._number = number               # my player number, values 0 to #players-1
        self._my_experience_cards = []      # list of ExperienceCards this player holds
        self._my_opportunity_cards = []     # list of OpportunityCards this player holds
        
        # dict where key is the degree program and the values the number of degrees attained
        # when number of degrees in any program >= 4, the can_retire flag is automatically set
        self._my_degrees = dict()
        # always start on Payday corner square
        self._board_location = BoardLocation(border_square_number=0, border_square_name="Payday", occupation_name=None, occupation_square_number=0 )
        self._can_retire = False
        self._is_insured = False
        self._is_unemployed = False         # True when player lands on (or is sent to) Unemployment
        self._is_sick = False               # True when player lands on Hospital
        
        # dict where key is occupation name, value is the number of completed trips
        # when completed trips >= 3, the can_retire flag is automatically set
        self._occupation_record = dict()
        
        self._opportunity_card = None   # the OpportunityCard instance of the card currently in play, or None otherwise
        self._experience_card = None    # the ExperienceCard instance of the card currently in play, or None otherwise
        self._laps = 0                  # the number of times player has passed or landed on Payday
        
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
    def cash(self):
        return self._cash
    
    @cash.setter
    def cash(self, value):
        self._cash = value
    
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
    def occupation_record(self):
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
    def board_location(self):
        return self._board_location
    
    @board_location.setter
    def board_location(self, value):
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
        return self._my_opportunitiy_cards
    
    @property
    def opportunity_card(self) -> OpportunityCard:
        """Returns the OpportunityCard currently in play, or None if no card is in play
        """
        return self._opportunity_card
    
    @opportunity_card.setter
    def opportunity_card(self, value:OpportunityCard):
        """Sets the OpportunityCard currently in play
        """
        self._opportunity_card = value
    
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
    def laps(self):
        return self._laps
    
    @laps.setter
    def laps(self, value):
        self._laps = value
    
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
                cards_dict[key] = {"quantity" : 1, "text" : card.text, "card" : cd}
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
                    cards_dict[key] = {"quantity" : 1, "spaces" : str(spaces), "card" : cd}
                else:
                    cards_dict[key] = {"quantity" : 1, "spaces" : card.type, "card" : cd}
        return cards_dict
                
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
        self._happiness.append(self.happiness + nhearts)
    
    def add_stars(self, nstars):
        self._fame.append(self.fame + nstars)
        
    def add_cash(self, money):  # could be a negative amount
        self.cash = self.cash + money
    
    def add_to_salary(self, money): #  again, could be negative amount
        self.salary = self.salary + money
        self._salary_history.append(self.salary)
        
    def total_points(self):
        return self.hapiness + self.fame + self.cash_points()
    
    def cash_points(self):
        """Cash points is the amount of cash/1000
        """
        return self.cash // 1000
    
    def is_complete(self):
        """Returns True if this players's total points are >= game total points, False otherwise
    
        """
        return  self.total_points() >= self.success_formula.total_points()
    

    def save(self):
        """Persist this player's state to a JSON file.
        File name is "player_" + player_initials + yyyy-mm-dd_hh:mm + _state.json"
        
        TODO finish this
        """
        today = datetime.now()
        fdate = '{0:d}-{1:02d}-{2:02d}_{3:02d}:{4:02d}:{5:02d}'.format(today.year,today.month, today.day, today.hour, today.minute, today.second)
        filename = "player_" + self._player_initials + fdate +" _state.json"
        #
        return filename
    
    def player_info(self, include_successFormula=False):
        fstring = f'salary:{self.salary}, Cash: {self.cash},  Fame: {self.fame},  Happiness: {self.happiness}, Is insured: {self.is_insured}'
        if include_successFormula:
            return f'{fstring}\nSuccess Formula: {self.success_formula}'
        else:
            return fstring
    
    def get_current_location(self) -> BoardLocation:
        """Gets the location of this player on the board.
            Returns: current_board_location
        
        """
        return  self.current_board_location
    
    def info(self):
        return  f' "name" : "{self.player_name}",  "number" : "{self.number}",  "initials" : "{self.player_initials}"'
    
    def __str__(self):
        fstring = f'Cash: {self.cash}  Fame: {self.fame}  Happiness: {self.happiness}'
        return f'{self.number}. {self.player_name} ({self.player_initials}) : salary:{self.salary}\n{fstring}\nSuccess Formula: {self.success_formula}'

    def to_JSON(self):
        sf = f'"SuccessFormula" : ' + '{\n    ' +  self._success_formula.to_JSON() + '\n  }'
        score = f' "cash" : "{self.cash}",  "fame" : "{self.fame}",  "hapiness" : "{self.happiness}", "is_insured: "{self.is_insured}" '
        locn =   self.board_location.to_JSON()

        jstr = f'{self.info()},\n {score},\n {locn},\n  {sf}'
        return  '{' + jstr + '\n}'
    
if __name__ == '__main__':
    player = Player(0, name='Don', initials='DWB')
    sf = SuccessFormula(stars=40, hearts=10, cash=50)
    player.success_formula = sf
    
    print(str(player))
    print(repr(player))
    
    player.add_cash(1000)
    player.add_hearts(3)
    player.add_stars(6)
    print("\n" + player.player_info(include_successFormula=False) )
    player.add_to_salary(2000)
    print("\n" + player.player_info(include_successFormula=True) + "\n" )
    
    print(player.to_JSON())
    