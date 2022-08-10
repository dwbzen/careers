'''
Created on Aug 9, 2022

@author: don_bacon
'''

class ExperienceCard(object):
    """
    Represents a single Experience card
    """

    def __init__(self, experience_card_type, spaces):
        """
        Constructor
        """
        self._card_type = experience_card_type
        self._spaces = spaces       # can be negative
        
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
