'''
Created on Aug 9, 2022

@author: don_bacon
'''
from enum import Enum

class OpportunityType(Enum):
    """Opportunity card types
    
    """
    OCCUPATION = 1
    OCCUPATION_CHOICE = 2
    BORDER = 3
    BORDER_CHOICE = 4
    ACTION = 5      # perform a non-movement action, qualified by ActionType
    TRAVEL = 6
    OPPORTUNITY = 7

    def __init__(self):
        self.card_types = {}
        self.card_types[OpportunityType.OCCUPATION] = "occupation"
        self.card_types[OpportunityType.OCCUPATION_CHOICE] = "occupation_choice"
        self.card_types[OpportunityType.BORDER] = "border_square"
        self.card_types[OpportunityType.BORDER_CHOICE] = "border_square_choice"
        self.card_types[OpportunityType.ACTION] = "action"
        self.card_types[OpportunityType.TRAVEL] = "travel"
        self.card_types[OpportunityType.OPPORTUNITY] = "opportunity"
        
    def describe(self):
        # self is the member here
        return self.name, self.value
    