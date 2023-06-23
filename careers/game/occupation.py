'''
Created on Aug 20, 2022

@author: don_bacon
'''
from game.occupationSquare import OccupationSquare
from typing import Dict

class Occupation(object):
    """Encapsulates a Careers Occupation.
    
    """


    def __init__(self, occupation_dict:dict, game=None):
        """
        An Occupation is loaded from the JSON file of the same name. The structure consists
            of two sections: "configuration" and "occupationSquares"
            The configuration section includes occupation meta-information used by the strategy plug-in.
            
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
        
        self._points = self._configuration.get('points', None)
        self._alternate_name = self._configuration.get('alternate_name', self._name)
        
        # if prior_experience ==1, entrance fee waived if previous experience (i.e. occupation completion)
        # otherwise entrance fee must be paid each time
        self._prior_experience = self._configuration.get('prior_experience', 1)
        # ranking relative to other occupations/professions
        self._ranking = self._configuration.get('ranking', {"points" : 0,"stars" : 0,"hearts" : 0, "cash" : 0, "salary" : 0, "overall" : 0})
        # number of potential experience and opportunity cards
        self._cards = self._configuration.get('cards', {"experience" : 0, "opportunity" : 0})
        # strategy
        self._strategy = self._configuration.get('strategy', {"danger_squares" : 2, "recommended_padding" : 3})
        # points is the number of potential points in the occupation. Cash and salary are in 1000's, so 5 points = $5,000
        self._points = self._configuration.get('points',{"cash" : 0,"stars" : 0,"hearts" : 0,"salary" : 0,"totalPoints" : 0})
        
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
        
    @property
    def entry_text(self):
        return self._entry_text
    
    @property
    def ranking(self) -> Dict:
        return self._ranking
    
    @property
    def cards(self) ->Dict:
        return self._cards
    
    @property
    def srategy(self) ->Dict:
        """Dictionary with the keys "danger_squares", "recommended_padding"
        """
        return self._srategy
    
    @property
    def points(self) ->Dict:
        """Dictionary with the keys "cash", "stars", "hearts", "salary", and "totalPoints"
        """
        return self._points
    
    @points.setter
    def points(self, value):
        self._points = value
    
    @property
    def prior_experience(self) ->int:
        return self._prior_experience
    
    @prior_experience.setter
    def prior_experience(self, value):
        self._prior_experience = value
        
    @property
    def alternate_name(self)->str:
        return self._alternate_name
    
    @alternate_name.setter
    def alternate_name(self, value):
        self._alternate_name = value
        