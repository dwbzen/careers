'''
Created on Aug 20, 2022

@author: don_bacon
'''
from game.occupationSquare import OccupationSquare

class Occupation(object):
    """Encapsulates a Careers Occupation.
    
    """


    def __init__(self, occupation_dict:dict, game=None):
        """
        Constructor
        """
        self._name = occupation_dict['name']
        self._configuration = occupation_dict['configuration']
        self._occupationClass = self._configuration['occupationClass']
        self._entry_fee = self._configuration['entry_fee']
        self._size = self._configuration['size']
        self._entry_square_number = self._configuration['entrance_square_number']
        self._exit_square_number = self._configuration['exit_square_number']
        self._entry_text = self._configuration['text']
        self._fullName = self._configuration['fullName']
        self._degreeRequirements = self._configuration.get('degreeRequirements', None)
        self._double_happiness = False      # this is temporarily set by a "double_happiness" Opportunity card
        self._careersGame = None
        #
        # avoids circular import
        #
        if game is not None:
            from game.careersGame import CareersGame
            assert isinstance(game,CareersGame)
            self._careersGame = game
        self._occupationSquares = self._create_occupation_squares(occupation_dict["occupationSquares"], self._careersGame)
        
    
    def _create_occupation_squares(self, occupationSquares:list, game) -> list:
        """For this Occupation create a list of OccupationSquare corresponding to the "occupationSquares".
            Returns: a List of  OccupationSquare
        """
        occupation_squares = list()
        for occupation_square_dict in occupationSquares:
            occupation_square = OccupationSquare(occupation_square_dict, game=game)
            occupation_squares.append(occupation_square)
        return occupation_squares
    
    @property
    def name(self):
        return self._name
    
    @property
    def occupationClass(self):
        return self._occupationClass
    
    @property
    def entry_fee(self) ->int:
        return self._entry_fee
    
    @entry_fee.setter
    def entry_fee(self, value:int):
        self._entry_fee = value
    
    @property
    def size(self):
        return self._size
    
    @property
    def entry_square_number(self):
        return self._entry_square_number
    
    @property
    def exit_square_number(self):
        return self._exit_square_number
    
    @property
    def fullName(self):
        return self._fullName
    
    @property
    def occupationSquares(self):
        return self._occupationSquares
    
    @property
    def degreeRequirements(self):
        return self._degreeRequirements
    
    @property
    def double_happiness(self):
        return self._double_happiness
    
    @double_happiness.setter
    def double_happiness(self, value):
        self._double_happiness = value
        
        