'''
Created on Aug 5, 2022

@author: don_bacon
'''
from game.successFormula import SuccessFormula
from game.careersObject import CareersObject
from datetime import datetime

class Player(CareersObject):
    
    def __init__(self, number=0, name="Player", salary=2000, cash=2000, initials="XXX"):
        self._player_name = name
        self._player_initials = initials
        self._salary_history = []                   # list of salaries the player has attained
        self.salary = salary                        # my current salary
        self._cash = cash                           # cash on hand
        self._success_formula = None        # my SuccessFormula
        self._happiness = [0]                # record of happiness (hearts) earned. Cumulative amounts, total is happiness[-1]
        self._fame = [0]                     # record of fame (stars) earned. Cumulative amounts, total is fame[-1]
        
        self._number = number               # my player number, values 0 to #players-1
        self._my_experience_cards = []      # list of ExperienceCard
        self._my_opportunitiy_cards = []    # list of OpportunityCard
        
        # dict where key is the degree program and the values the number of degrees attained
        # when number of degrees in any program >= 4, the can_retire flag is automatically set
        self._my_degrees = dict()
        self._current_border_square_number = 0     # the border square# this player currently occupies
        self._current_occupation_name = None            # the name of occupation the player is currently in
        self._current_occupation_square_number = 0      # the square number within that occupation (if name is not None)
        self._can_retire = False
        self._has_insurance = False
        
        # dict where key is occupation name, value is the number of completed trips
        # when completed trips >= 3, the can_retire flag is automatically set
        self._occupation_record = dict()
        
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
    def has_insurance(self):
        return self._has_insurance
    
    @has_insurance.setter
    def has_insurance(self, value:bool):
        self._has_insurance = value
    
    @property
    def happiness(self):
        return self._happiness[-1]
    
    @property   
    def fame(self):
        return self._fame[-1]
    
    @property
    def current_border_square_number(self):
        return self._current_border_square_number
    
    @property
    def current_occupation_name(self):
        return self._current_occupation_name
    
    @property
    def current_occupation_square_number(self):
        return self._current_occupation_square_number
    
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
        fstring = f'salary:{self.salary}, Cash: {self.cash},  Fame: {self.fame},  Happiness: {self.happiness}'
        if include_successFormula:
            return f'{fstring}\nSuccess Formula: {self.success_formula}'
        else:
            return fstring
    
    def get_current_location(self):
        """Gets the location of this player on the board.
            Returns: a 3-tupple: (current_border_square_number, current_occupation_name, current_occupation_board_number)
        
        """
        return  (self.current_border_square_number, self.current_occupation_name, self.current_occupation_square_number)
    
    def __str__(self):
        fstring = f'Cash: {self.cash}  Fame: {self.fame}  Happiness: {self.happiness}'
        return f'{self.number}. {self.player_name} ({self.player_initials}) : salary:{self.salary}\n{fstring}\nSuccess Formula: {self.success_formula}'

    def to_JSON(self):
        sf = f'"SuccessFormula" : ' + '{\n    ' +  self._success_formula.to_JSON() + '\n  }'
        score = f'"cash" : "{self.cash}",  "fame" : "{self.fame}",  "hapiness" : "{self.happiness}"'
        jstr = f' "name" : "{self.player_name}",  "number" : "{self.number}",  "initials" : "{self.player_initials}",\n  {score},\n  {sf}'
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
    print("\n" + player.player_info(include_successFormula=True) )
    