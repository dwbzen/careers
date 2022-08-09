'''
Created on Aug 9, 2022

@author: don_bacon
'''
from careers.game import ExperienceCardType

class ExperienceCard(object):
    """
    Represents a single Experience card
    """

    def __init__(self, atype=ExperienceCardType.FIXED, spaces=0):
        """
        Constructor
        """
        self._card_type = atype
        self._spaces = spaces       # can be negative
        
    @property
    def card_type(self) -> ExperienceCardType:
        return self._card_type
    
    @card_type.setter
    def card_type(self, ct:ExperienceCardType) :
        self._card_type = ct
        
    @property
    def spaces(self) -> int:
        return self._spaces
    
    @spaces.setter
    def spaces(self, spaces:int):
        self._spaces = spaces
