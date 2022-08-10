'''
Created on Aug 9, 2022

@author: don_bacon
'''

from enum import Enum
class ActionType(Enum):
    """Action types referenced on Opportunity cards, occupation and border squares
    
    """
    EXTRA_TURN = 1          # player gets an extra turn
    LEAVE_UNEMPLOYMENT = 2  # player can leave unemployment without penalty
    COLLECT_EXPERIENCE = 3  # collect experience card from other players
    DRAW_EXPERIENCE = 4     # draw an experience card from the deck
    DRAW_OPPORTUNITY = 5    # draw an opportunity card from the deck

    def describe(self):
        # self is the member here
        return self.name, self.value
    