'''
Created on Aug 9, 2022

@author: don_bacon
'''

from game.careersObject import CareersObject
from game.gameConstants import PendingActionType, GameConstants
from enum import Enum
import json

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
    
class OpportunitySpecialProcessingType(Enum):
    BUY_INSURANCE = "buy_insurance"
    SELECT_EXPERIENCE = "select_experience"
    CHOOSE_OCCUPATION = "choose_occupation"
    CHOOSE_DESTINATION = "choose_destination"
    
    
class OpportunityCard(CareersObject):
    """
    Represents a single Opportunity card
    """

    def __init__(self, opportunity_type:str, number:int, ncard:int, destination:str=None, text="", expenses_paid=False, double_happiness=False, action_type=None, special_processing=None):
        """Constructor
            Arguments:
                opportunity_type - the OpportunityType of this card. key: "card_type"
                number - the unique number identifying this card. key: "number"
                ncard - the ordinal of this type of card (from 0 to quantity-1). key:
                destination - the "name" of the corresponding border square if there is a destination, otherwise None. key: "destination"
                text - the Opportunity card text. key: "text"
                expenses_paid - Applies to OpportunityType.OCCUPATION: True if the player can enter for free. key: "expenses_paid"
                double_happiness - Applies to OpportunityType.OCCUPATION: True if happiness point values are doubled. key: "double_happiness"
                action_type - OpportunityActionType or None. key: "action_type"
                special_processing - the special_processing associated with this card or None. key: "special_processing"
                    If present, consists of a OpportunitySpecialProcessingType (key: "type" as a string)
                    PendingActionType (key: "pending_action" as a string)
                
        """
        self._opportunity_type = OpportunityType[opportunity_type.upper()]
        self._action_type = None if action_type is None else OpportunityActionType[action_type.upper()]
        if destination == "":
            self._destination = None
        else:
            self._destination = destination
        if "<HAPPINESS>" in text:
            text = text.replace("<HAPPINESS>", f"{GameConstants.HAPPINESS.title()}")
        if "<FAME>" in text:
            text = text.replace("<FAME>", f"{GameConstants.FAME.title()}")
        self._text = text
        self._expenses_paid = expenses_paid
        self._double_happiness = double_happiness
        self._ncard = ncard
        self._number = number
        self._special_processing_dict = None
        self._value = 0    # determined by card_type
        
        if special_processing is not None:
            self._special_processing_dict = special_processing
            self._special_processing_type = OpportunitySpecialProcessingType[special_processing['type'].upper()]
            pa = special_processing.get('pending_action', None)
            self._pending_action = PendingActionType[pa.upper()] if pa is not None else None
        else:
            self._special_processing_type = None
            self._pending_action = None
        
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
    def double_happiness(self) -> bool:
        return self._double_happiness
    
    @double_happiness.setter
    def double_happiness(self, dh:bool):
        self._double_happiness = dh

    @property
    def action_type(self) ->OpportunityActionType:
        return self._action_type
    
    @action_type.setter
    def action_type(self, value:OpportunityActionType):
        self._action_type = value
        
    @property
    def ncard(self) ->int:
        return self._ncard
    
    @property
    def number(self) -> int:
        return self._number

    @property
    def special_processing_type(self) -> OpportunitySpecialProcessingType | None:
        return self._special_processing_type

    @property
    def pending_action(self) ->PendingActionType | None:
        return self._pending_action
    
    @property
    def value(self) ->int:
        return self._value
    
    @value.setter
    def value(self, val):
        self._value = val

    def __str__(self):
        return f'{self.text} ({self.number})'
    
    def to_dict(self) ->dict:
        cd = {"card_type": self.opportunity_type.value}
        cd["number"] = self.number
        cd['text'] = self.text
        cd["value"] = self.value
        
        if self.action_type is not None:
            cd['action_type'] = self.action_type.value
        if self._special_processing_dict is not None:
            cd['special_processing'] = self._special_processing_dict
        return cd
    
    def to_JSON(self) ->str:
        return json.dumps(self.to_dict())
    
    