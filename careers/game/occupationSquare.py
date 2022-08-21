'''
Created on Aug 14, 2022

@author: don_bacon
'''
from game.gameSquare import GameSquare
from game.player import Player
from game.commandResult import CommandResult

class OccupationSquare(GameSquare):
    '''
    classdocs
    '''


    def __init__(self, occupation_square_dict):
        """ Create an OccupationSquare
        
        """
        super().__init__("Occupation", name=None, number= occupation_square_dict['number'], \
                         text=occupation_square_dict['text'], special_processing_dict=occupation_square_dict['specialProcessing'])
        
        self._game_square_dict = occupation_square_dict
        self._stars = occupation_square_dict["stars"]
        self._hearts = occupation_square_dict["hearts"]
        self._experience = occupation_square_dict["experience"]         # the number of Experience cards to collect on this square
        self._opportunities = occupation_square_dict["opportunities"]   # the number of Opportunity cards to collect on this square
        self._action_text = occupation_square_dict['action_text']
        self._bonus = occupation_square_dict.get('bonus',0)
        
    @property
    def stars(self):
        return self._stars
    
    @property
    def hearts(self):
        return self._hearts
    
    @property
    def experience(self):
        return self._experience
    
    @property
    def opportunities(self):
        return self._opportunities
    
    @property
    def action_text(self):
        return self._action_text
    
    def execute(self, player:Player) -> CommandResult:
        """Executes the actions associated with this occupation square for a given Player
            Returns: CommandResult
        """
        result = CommandResult(0, "TODO", False)   #  TODO
        return result
    
    
    def to_JSON(self):
        txt = f'''{{
        "square_class" : "{self.square_class}",
        "name":{self.name},
        "number":"{self.number}",
        "text":"{self.text}",
        "stars":"{self.stars}",
        "hearts":"{self.hearts}",
        "experience":"{self.experience}",
        "opportunities":"{self.opportunities}",
        "action_text":"{self.action_text}",
        "special_processing_txt" : {self._special_processing_dict} 
        }}'''
        return txt
        
    