'''
Created on Aug 12, 2022

@author: don_bacon
'''

from game.careersObject import CareersObject
import json
from typing import Dict, List, Union

class SpecialProcessing(CareersObject):
    """Encapsulates the "specialProcessing" section of a border square or occupation square.
        This is only a model class. The actual processing is done by CareersGameEngine.
    """
    
    border_types = ["payday", "opportunity", "payTax", "enterOccupation", "enterCollege", "buyHearts", "buyStars", "buyExperience",\
                    "hospital", "unemployment", "buyInsurance", "gamble" ]

    occupation_types = ["shortcut", "cashLossOrUnemployment", "goto",\
                         "salaryIncrease", "salaryCut", "bonus", "favors", "backstab", "fameLoss", "hapinessLoss"]
    
    common_types = ["travelBorder", "cashLoss", "extraTurn", "loseNextTurn"]
    
    all_types = border_types + occupation_types + common_types
    
    SPECIAL_PROCESSING = Dict[str, Union[str, List[int], int, float, Dict[str, int]]]

    def __init__(self, special_processing_dict:SPECIAL_PROCESSING, square_type:str):
        """Constructor
            Arguments:
                special_processing_dict - the JSON specialProcessing section of a border or occupation square as a dictionary
                square_type - "occupation" or "border"
        """
        self._special_processing_dict = special_processing_dict
        #
        # mandatory elements
        #
        self._square_type = square_type     # "occupation" or "border"
        self._processing_type = special_processing_dict["type"]     # must be one of the above types
        #
        # optional elements which are type-dependent
        # an 'amount' can be a numeric type (int or float), a string or a dictionary
        #
        self._amount = 0            # a discrete money amount which may be salary or cash depending on type
        self._amount_dict = None
        self._amount_str = ""
        amt = special_processing_dict.get('amount', 0)    # 'amount' can be a number or a string or a dictionary
        if isinstance(amt, int) or isinstance(amt, float):
            self._amount = amt
        elif isinstance(amt, str):
            self._amount_str = amt
        else:
            self._amount_dict = amt    # how a money amount is calculated
        
        self._dice = special_processing_dict.get('dice', 0)                 # number of dice used to calculate some amount
        self._of = special_processing_dict.get('dice', 'cash')              # cash (cash-on-hand) or salary
        self._penalty = special_processing_dict.get('penalty', 0)           # a loss quantity (hearts or stars)
        self._limit = special_processing_dict.get('limit', None)            # a limiting factor, usually "salary" (in 1000s)
        
        # square number to advance to, relative to the overall game layout or occupation
        self._next_square = special_processing_dict.get('next_square', None)    

        self._destination = special_processing_dict.get('destinationOccupation', None)  # the name of a destination occupation
        self._percent = special_processing_dict.get('percent', 0.0)                     # a percent amount of salary or cash depending on type
        self._must_roll = special_processing_dict.get('must_roll', [])                  # a list of numbers that must be rolled in order to leave this square
        self._require_doubles = special_processing_dict.get('require_doubles', 0)==1
        self._hearts = special_processing_dict.get('hearts', [])                        # used for holiday type, a 2-element list
        self._tax_table = special_processing_dict.get('taxTable', None)    # format is upper limit : % amount, for example { 3000 : 0.2 } if you make <= 3000/yr, take 20% as tax
        self._pending_action = special_processing_dict.get('pending_action', None) 
    
    @property
    def square_type(self):
        return self._square_type
    
    @property
    def processing_type(self):
        return self._processing_type
    
    @property
    def amount(self):
        return self._amount
    
    @property
    def amount_dict(self):
        return self._amount_dict
    
    @property
    def amount_str(self):
        return self._amount_str
    
    @property
    def destination(self):
        return self._destination
    
    @property
    def dice(self):
        return self._dice
    
    @property
    def limit(self):
        return self._limit
    
    @property
    def next_square(self):
        return self._next_square
    
    @property
    def penalty(self):
        return self._penalty
    
    @property
    def percent(self):
        return self._percent
    
    @property
    def must_roll(self):
        return self._must_roll
    
    @property
    def require_doubles(self):
        return self._require_doubles
    
    @property
    def hearts(self) -> list:
        return self._hearts
    
    @property
    def pending_action(self):
        return self._pending_action
    
    @pending_action.setter
    def pending_action(self, value):
        self._pending_action = value
    
    @property
    def of(self):
        return self._of
    
    @property
    def tax_table(self):
        return self._tax_table
    
    def __str__(self):
        return str(self._special_processing_dict)
    
    def to_JSON(self):
        return json.dump(self._special_processing_dict, indent=2)
