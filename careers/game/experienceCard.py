'''
Created on Aug 9, 2022

@author: don_bacon
'''

from game.commandResult import CommandResult
from game.player import Player

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
        
    def execute(self, player:Player) -> CommandResult:
        """Execute the actions associated with this Experience card, which is forward or backward movement in place of a roll.
            Needs to handle three types of wild cards.
            Returns: CommandResult
        """
        result = CommandResult(0, "TODO", False)   #  TODO
        return result
    
    