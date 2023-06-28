'''
Created on Aug 9, 2022

@author: don_bacon
'''

from game.careersObject import CareersObject
from enum import Enum
import json
from typing import List

class ExperienceType(Enum):
    FIXED = "fixed"
    ONE_DIE_WILD = "one_die_wild"
    TWO_DIE_WILD = "two_die_wild"
    TRIPLE_WILD = "triple_wild"

class ExperienceCard(CareersObject):
    """
    Represents a single Experience card
    """
    
    card_types = [ "fixed", "one_die_wild", "two_die_wild", "triple_wild" ]

    def __init__(self, number:int, ncard:int, experience_card_type:str, spaces:int):
        """
        Constructor
            Arguments:
                number - the unique number identifying this card
                experience_card_type - the type of this card, one of card_types: "fixed",  "one_die_wild", "two_die_wild", "triple_wild"
                spaces - the number of spaces to move, can be negative to move backwards.
                         spaces == 0 indicates a "wild" card as identified by experience_card_type
                ncard - the ordinal of this type of card (from 0 to quantity-1)
        """
        self._number = number
        self._card_type = ExperienceType[experience_card_type.upper()]
        self._spaces = spaces       # can be negative
        self._ncard = ncard
        self._value = 0    # determined by card_type
        if self._card_type is ExperienceType.FIXED:
            self._range = list(range(1,8))
        elif self._card_type is ExperienceType.ONE_DIE_WILD:
            self._range = list(range(1,7))
        elif self._card_type is ExperienceType.TWO_DIE_WILD:
            self._range = list(range(2,13))
        elif self._card_type is ExperienceType.TRIPLE_WILD:
            self._range = list(range(1,13))        # 1 to 6 on an occupation path, 2 to 12 on a border square
        
    @property
    def card_type(self) -> ExperienceType:
        return self._card_type
    
    @card_type.setter
    def card_type(self, ct:ExperienceType) :
        self._card_type = ct
        
    @property
    def spaces(self) -> int:
        return self._spaces
    
    @spaces.setter
    def spaces(self, spaces:int):
        self._spaces = spaces
    
    @property
    def number(self):
        return self._number

    @property
    def ncard(self):
        return self._ncard
    
    @property
    def range(self) ->List[int]:
        return self._range
    
    @property
    def value(self) ->int:
        return self._value
    
    @value.setter
    def value(self, val):
        self._value = val

    def __str__(self):
        if self.card_type is ExperienceType.FIXED:
            return f'{self.spaces} spaces'
        else:
            return self.card_type.value
        
    def to_dict(self, include_range=True):
        cd = {"type":"experience", "number":self.number}
        cd["spaces"] = self.spaces
        cd["card_type"] = self.card_type.value
        cd["value"] =self.value
        
        if include_range:
            if self.card_type is ExperienceType.FIXED:
                cd["range"] = list(range(self.spaces, self.spaces+1))
            else:
                cd["range"] = self.range

        return cd

    def to_JSON(self):
        return json.dumps(self.to_dict())
    
    