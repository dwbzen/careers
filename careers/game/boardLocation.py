'''
Created on Aug 24, 2022

@author: don_bacon
'''
from game.careersObject import CareersObject
import json

class BoardLocation(CareersObject):
    """Defines a position on the game board.
        Board location is defined by 4 properties:
            border_square_number - the border square number which is in the range(0, game_board_size +1)
            occupation_name - the Occupation name IF the player is currently on an occupation path, else None
            occupation_square_number - if occupation_name is not None, the square number of that occupation
            border_square_name - (optional) if not None the name of this border square (from the game layout)
            json_string - JSON representation, optional.
        
        NOTE that if the player is on an occupation path, the border_square_number will be
        the border square number of that occupation's entrance square.
    
    """

    def __init__(self, border_square_number=0, border_square_name=None, occupation_name=None, occupation_square_number=0, json_string=None):
        """
        Constructor
        """
        if json_string is not None:
            self.from_JSON(json_string)
        else:
            self._border_square_number = border_square_number
            self._border_square_name = border_square_name
            self._occupation_name = occupation_name
            self._occupation_square_number = occupation_square_number
    
    def from_JSON(self, jstr):
        bs_dict = json.loads(jstr)    # this could raise a TypeError
        self.border_square_number = bs_dict['border_square_number']
        self.border_square_name = bs_dict['border_square_name']
        self.occupation_name = bs_dict['occupation_name']
        self.occupation_square_number = bs_dict['occupation_square_number']
    
    @property
    def border_square_number(self):
        return self._border_square_number
    
    @border_square_number.setter
    def border_square_number(self, value):
        self._border_square_number = value
        
    @property
    def occupation_name(self):
        return self._occupation_name
    
    @occupation_name.setter
    def occupation_name(self, value):
        self._occupation_name = value
        
    @property
    def occupation_square_number(self):
        return self._occupation_square_number
    
    @occupation_square_number.setter
    def occupation_square_number(self, value):
        self._occupation_square_number = value
        
    @property
    def border_square_name(self):
        return self._border_square_name
    
    @border_square_name.setter
    def border_square_name(self, value):
        self._border_square_name = value
    
    def __str__(self):
        locn = f'Border square#: {self.border_square_number}'
        if self.border_square_name is not None:
            locn += f'  "{self.border_square_name}"'
        if self.occupation_name is not None:
            locn += f'\tOccupation: {self.occupation_name}   square#: {self._occupation_square_number}'
        return locn
    
    def to_JSON(self):
        jstr = f'{{\n  "border_square_number" : "{self.border_square_number}",\n'
        jstr += f'  "border_square_name" : "{self.border_square_name}",\n'
        jstr += f'  "occupation_square_number" : "{self.occupation_square_number}",\n'
        jstr += f'  "occupation_name" : "{self.occupation_name}"\n}}'
        return jstr
    
