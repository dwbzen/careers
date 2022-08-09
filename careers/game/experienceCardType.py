'''
Created on Aug 9, 2022

@author: don_bacon
'''

from enum import Enum
class ExperienceCardType(Enum):
    """
    Experience card types
    """
    FIXED = 1
    SINGLE_DIE_WILD = 2
    DOUBLE_DIE_WILD = 3
    TRIPLE_DIE_WILD = 4

    def __init__(self, params):
        self.card_types = {}
        self.card_types[ExperienceCardType.FIXED] = "fixed"
        self.card_types[ExperienceCardType.SINGLE_DIE_WILD] = "1-die wild"
        self.card_types[ExperienceCardType.DOUBLE_DIE_WILD] = "2-die wild"
        self.card_types[ExperienceCardType.TRIPLE_DIE_WILD] = "triple wild"
        
    def describe(self):
        # self is the member here
        return self.name, self.value
        