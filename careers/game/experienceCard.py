'''
Created on Aug 9, 2022

@author: don_bacon
'''

from game.careersObject import CareersObject

class ExperienceCard(CareersObject):
    """
    Represents a single Experience card
    """
    
    card_types = [ "fixed", "1-die wild", "2-dice wild", "triple wild" ]

    def __init__(self, number, ncard, experience_card_type, spaces):
        """
        Constructor
            Arguments:
                number - the unique number identifying this card
                experience_card_type - the type of this card, one of card_types: "fixed", "1-die wild", "2-dice wild", "triple wild" 
                spaces - the number of spaces to move, can be negative to move backwards.
                         spaces == 0 indicates a "wild" card as identified by experience_card_type
                ncard - the ordinal of this type of card (from 0 to quantity-1)
        """
        self._number = number
        self._card_type = experience_card_type
        self._spaces = spaces       # can be negative
        self._ncard = ncard
        
    @property
    def card_type(self) -> str:
        return self._card_type
    
    @card_type.setter
    def card_type(self, ct:str) :
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

    def __str__(self):
        if self.card_type == 'fixed':
            return f'{self.spaces} spaces'
        else:
            return self.card_type

    def to_JSON(self):
        jtxt = f'{{"number" : "{self.number}", '
        if self.card_type == 'fixed':
            jtxt += f'"spaces" : "{self.spaces}" }}'
        elif self.card_type == '1-die wild':
            jtxt += f'"spaces" : "?" }}'
        elif self.card_type == '2-die wild':
            jtxt += f'"spaces" : "??" }}'
        elif self.card_type == '3-die wild':
            jtxt += f'"spaces" : "???" }}'
        
        return jtxt
    
    