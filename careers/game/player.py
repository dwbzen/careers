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
        self.salary = salary
        self._cash = cash                           # cash on hand
        self._success_formula = SuccessFormula()    # default values
        self._number = number               # my player number, values 0 to #players-1
        self._my_experience_cards = []      # list of ExperienceCard
        self._my_opportunitiy_cards = []    # list of OpportunityCard
        self._my_degrees = []               # list of dict where key is the degree program and the values the number of degrees attained
        self._current_square_number = 0     # the border square# this player currently occupies
        self._current_occupation_name = None            # the name of occupation the player is currently in
        self._current_occupation_square_number = 0      # the square number within that occupation (if name is not None)
        self._can_retire = False           
        
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
    def can_retire(self):
        return self._can_retire
    
    def add_degree(self, degree_program):
        if degree_program in self.my_degrees:
            count = self.my_degrees[degree_program]
            # max of 4 degrees in any degree program
            if count <= 4:
                count += 1
                self._my_degrees[degree_program] = count
            if count >= 3:
                self._can_retire = True
        else:
            self._my_degrees[degree_program] = 1
        
    def add_hearts(self, nhearts):
        self.hearts = self.hearts + nhearts
    
    def add_stars(self, nstars):
        self.stars = self.stars + nstars
        
    def add_cash(self, money):  # could be a negative amount
        self.cash = self.cash + money
    
    def add_to_salary(self, money): #  again, could be negative amount
        self.salary = self.salary + money
        
    def total_points(self):
        return self.hearts + self.stars + self.cash_points()
    
    def cash_points(self):
        """Cash points is the amount of cash/1000
        
        """
        return self.cash // 1000
    
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
    
    def __str__(self):
        return f'{self.number}. {self.player_name} ({self.player_initials}) : salary:{self.salary}, cash:{self.cash}, formula: {self.success_formula}'
    
    def __repr__(self):
        """Returns the JSON representation of this player
        
        """
        pass
    
    def to_JSON(self):
        return self.__repr__()
    
    def is_complete(self):
        """Returns True if this players's total points are >= game total points, False otherwise
    
        """
        return  self.total_points() >= self.success_formula.total_points()
    
if __name__ == '__main__':
    player = Player(0, name='Don', initials='DWB')
    sf = SuccessFormula(stars=40, hearts=10, cash=50)
    player.success_formula = sf
    print(str(player.success_formula))
    
    print(str(player))
    
    
    