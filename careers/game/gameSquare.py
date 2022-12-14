'''
Created on Aug 14, 2022

@author: don_bacon
'''

from game.specialProcessing import SpecialProcessing
from game.careersObject import CareersObject
from game.player import Player
from game.commandResult import CommandResult
from game.gameParameters import GameParameters

from enum import Enum
from typing import Dict, Union


class GameSquareClass(Enum):
    BORDER = 'Border'
    OCCUPATION = 'Occupation'

class GameSquare(CareersObject):
    """Represents a square a player can land on. This can be a Border or Occupation.
    
    """
    
    GAME_SQUARE = Dict[str, Union[int, str, SpecialProcessing.SPECIAL_PROCESSING ]]
    
    def __init__(self, square_class:str, name=None, number=-1, text=None, special_processing_dict=None, action_text=None, game=None):
        """Create a GameSquare
        
        """
        self._square_class = GameSquareClass[square_class.upper()]
        self._name = name
        self._number = number
        self._text = text
        self._action_text = action_text
        self._special_processing_dict = special_processing_dict
        self._game_square_dict = None       # populated by concrete class
        self._square_type = None            # populated by concrete class
        self._special_processing = SpecialProcessing(special_processing_dict, square_class) if special_processing_dict is not None and len(special_processing_dict) > 0 else None
        self._careersGame = None
        self._game_parameters = None
        self._help_text = None    # optional "help_text" content
        #
        # avoids circular import
        #
        assert(game is not None)
        if game is not None:
            from game.careersGame import CareersGame
            assert isinstance(game,CareersGame)
            self._careersGame = game
            self._game_parameters = game.game_parameters    # GameParameters instance
            if self._special_processing is not None:        # not all game squares have SpecialProcessing
                self._special_processing.game_parameters = self._game_parameters
        
    @property
    def square_type(self):
        return self._square_type
    
    @square_type.setter
    def square_type(self, value):
        self._square_type = value

    @property
    def square_class(self) -> GameSquareClass:
        """Border or Occupation
        """
        return self._square_class
    
    @square_class.setter
    def square_class(self, value:GameSquareClass):
        if value is not None:
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
    
    @property
    def action_text(self):
        return self._action_text
    
    @action_text.setter
    def action_text(self, value):
        self._action_text = value
        
    @property
    def special_processing(self):
        return self._special_processing
    
    @property
    def careersGame(self):
        return self._careersGame
    
    @property
    def game_parameters(self) -> GameParameters:
        return self._game_parameters
    
    @property
    def help_text(self) -> str:
        return self._help_text
    
    @help_text.setter
    def help_text(self, text:str):
        self._help_text = text
    
    def execute(self, player:Player) -> CommandResult:
        """Execute actions associated with this Occupation or Border square
            Override in derived class. Base implementation returns None.
        
        """
        return None
    
    def execute_special_processing(self, player):
        """Invokes the specialProcessing section of this game square for a player.
            This method is called as exit processing for a square, whereas execute() is called when a player lands on a square.
            Override in derived class. Base implementation returns None.
        """
        return None
        
    def to_JSON(self):
        #
        # override in derived class
        #
        return None
    