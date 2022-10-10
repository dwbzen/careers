'''
Created on Aug 9, 2022

@author: don_bacon
'''

from game.careersObject import CareersObject
from enum import Enum

class OpportunityType(Enum):
    OCCUPATION              = 'occupation'
    OCCUPATION_CHOICE       = 'occupation_choice'
    BORDER_SQUARE           = 'border_square'
    BORDER_SQUARE_CHOICE    = 'border_square_choice'
    ACTION                  = 'action'
    OPPORTUNITY             = 'opportunity'
    TRAVEL                  = 'travel'
    
class OpportunityActionType(Enum):
    COLLECT_EXPERIENCE  = 'collect_experience'
    EXTRA_TURN          = 'extra_turn'
    LEAVE_UNEMPLOYMENT  = 'leave_unemployment'
    
    
class OpportunityCard(CareersObject):
    """
    Represents a single Opportunity card
    """

    def __init__(self, opportunity_type:str, number:int, ncard:int, destination:str=None, text="", expenses_paid=False, double_happiness=False, action_type=None):
        """Constructor
            Arguments:
                opportunity_type - the OpportunityType of this card
                number - the unique number identifying this card
                ncard - the ordinal of this type of card (from 0 to quantity-1)
                destination - the "name" of the corresponding border square if there is a destination, otherwise None
                text - the Opportunity card text
                expenses_paid - Applies to OpportunityType.OCCUPATION: True if the player can enter for free.
                double_happiness - Applies to OpportunityType.OCCUPATION: True if happiness point values are doubled.
        """
        self._opportunity_type = OpportunityType[opportunity_type.upper()]
        self._action_type = None if action_type is None else OpportunityActionType[action_type.upper()]
        if destination == "":
            self._destination = None
        else:
            self._destination = destination
        self._text = text
        self._expenses_paid = expenses_paid
        self._double_happiness = double_happiness
        self._action_type = None
        self._ncard = ncard
        self._number = number
        
    @property
    def opportunity_type(self) ->str:
        return self._opportunity_type
    
    @opportunity_type.setter
    def opportunity_type(self, ctype:str):
        self._opportunity_type = ctype
    
    @property
    def destination(self):
        return self._destination
    
    @destination.setter
    def destination(self, bs):
        self._destination = bs
    
    @property
    def text(self):
        return self._text
    
    @text.setter
    def text(self, text):
        self._text = text
    
    @property
    def expenses_paid(self):
        return self._expenses_paid
    
    @expenses_paid.setter
    def expenses_paid(self, ep):
        self._expenses_paid = ep
    
    @property
    def double_happiness(self):
        return self._double_happiness
    
    @double_happiness.setter
    def double_happiness(self, dh):
        self._double_happiness = dh

    @property
    def action_type(self):
        return self._action_type
    
    @action_type.setter
    def action_type(self, value):
        self._action_type = value
        
    @property
    def ncard(self):
        return self._ncard
    
    @property
    def number(self):
        return self._number

    def __str__(self):
        return self.text
    
    def to_JSON(self):
        jtxt = f'{{"number" : "{self.number}", '
        jtxt += f'"text" : "{self.text}" }}'
        return jtxt
    
    