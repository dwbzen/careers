'''
Created on Aug 12, 2022

@author: don_bacon
'''

from game.gameSquare import GameSquare
from game.player import Player
from game.commandResult import CommandResult

class BorderSquare(GameSquare):
    """Encapsulates a Careers game border (non-occupation) square.
    Border squares are numbered consecutively starting with 0 (Payday by convention).
    They also have a name which may not be unique. For example, there are 12 squares named "Opportunity"
    The border square "type" is enumerated in the gameLayout JSON as "types_list
    """

    types_list = ["corner_square", "opportunity_square", "danger_square", "travel_square", "occupation_entrance_square", "action_square"]

    def __init__(self, border_square_dict):
        """
        Constructor
        """
        super().__init__("Border", name=border_square_dict['name'], number= border_square_dict['number'], \
                         text=border_square_dict['text'], special_processing_dict=border_square_dict['specialProcessing'])
        
        self._game_square_dict = border_square_dict
        self._square_type = border_square_dict['type']
        
    @property
    def square_type(self):
        return self._square_type
    
    def execute(self, player:Player) -> CommandResult:
        """Execute the actions associated with this BorderSquare. Overrides GameSquare.execute().
            Assumes the Player's current location is this BorderSquare.
            Returns: CommandResult
        """
        result = CommandResult(0, "TODO", False)   #  TODO
        return result
        
    def to_JSON(self):
        txt = f'''{{
        "square_class" : "{self.square_class}",
        "name":"{self.name}",
        "number":"{self.number}",
        "text":"{self.text}",
        "type":"{self.square_type}",
        "special_processing_txt" : {self._special_processing_dict} 
        }}'''
        return txt

    
    