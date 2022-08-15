'''
Created on Aug 14, 2022

@author: don_bacon
'''

from game.specialProcessing import SpecialProcessing
from game.careersObject import CareersObject

class GameSquare(CareersObject):
    """Represents a square a player can land on. This can be a Border or Occupation.
    
    """

    def __init__(self, square_class:str, name=None, number=-1, text=None, special_processing_dict = None):
        """Create a GameSquare
        
        """
        self._square_class = square_class
        self._name = name
        self._number = number
        self._text = text
        self._special_processing_dict = special_processing_dict
        self._game_square_dict = None       # populated by concrete class
        if special_processing_dict is not None and len(special_processing_dict) > 0:
            self._special_processing = SpecialProcessing(special_processing_dict, square_class)
        
    @property
    def square_class(self):
        """Border or Occupation
        
        """
        return self._square_class
    
    @square_class.setter
    def square_class(self, value):
        if value is not None and ( value == 'Border' or value == 'Occupation'):
            self._square_class = value
        else: raise(ValueError("Invalid square class: " + value))
    
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        self._name = value
        
    @property
    def number(self):
        return self._number
    
    @number.setter
    def number(self, value):
        self._number = value
        
    @property
    def text(self):
        return self._text
    
    @text.setter
    def text(self, value):
        self._text = value
        
    def to_JSON(self):
        #
        # override in child class
        #
        return None
    