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
        self._current_square_number = 0     # the border square# this player currently occupies
        self._current_occupation_name = None            # the name of occupation the player is currently in
        self._current_occupation_square_number = 0      # the square number within that occupation (if name is not None)
        
        
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
        
    
    def save(self):
        """Persist this player's state to a JSON file.
        File name is "player_" + player_initials + yyyy-mm-dd_hh:mm + _state.json"
        
        TODO finish this
        """
        today = datetime.now()
        fdate = '{0:d}-{1:02d}-{2:02d}_{3:02d}:{4:02d}:{5:02d}'.format(today.year,today.month, today.day, today.hour, today.minute, today.second)
        filename = "player_" + self._player_initials + fdate +" _state.json"
        #
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
        return self.success_formula.is_complete()
    
if __name__ == '__main__':
    player = Player(0, name='Don', initials='DWB')
    sf = SuccessFormula(stars=40, hearts=10, cash=50)
    player.success_formula = sf
    print(str(player.success_formula))
    
    print(str(player))
    
    
    