'''
Created on Aug 5, 2022

@author: don_bacon
'''
from game.successFormula import SuccessFormula
from datetime import datetime

class Player(object):
    
    def __init__(self, name="Player", salary=2000, cash=2000, initials="xxx"):
        self._player_name = name
        self._player_initials = initials
        self._salary = salary
        self._cash = cash
        self._success_formula = SuccessFormula()     # default values
        
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
    
    @property
    def cash(self):
        return self._cash
    
    @property
    def success_formula(self):
        return self._success_formula
    
    @success_formula.setter
    def success_formula(self, value):
        self._success_formula = value
    
    def save(self):
        """Persist this player's state to a JSON file.
        File name is "player_" + player_initials + yyyy-mm-dd_hh:mm + _state.json"
        
        TODO finish this
        """
        today = datetime.now()
        fdate = '{0:d}-{1:02d}-{2:02d}_{3:02d}:{4:02d}:{5:02d}'.format(today.year,today.month, today.day, today.hour, today.minute, today.second)
        filename = "player_" + self._player_initials + fdate +" _state.json"
        return filename
    

if __name__ == '__main__':
    player = Player(name='Don', initials='DWB')
    sf = SuccessFormula(stars=40, hearts=10, cash=50)
    player.success_formula = sf
    
    print(str(player.success_formula))
    
    print(f' cash: {player.cash}')
    
    
    