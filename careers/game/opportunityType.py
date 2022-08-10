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
        
    def describe(self):
        # self is the member here
        return self.name, self.value
    