'''
Created on Nov 25, 2022

@author: don_bacon
'''
from game.careersObject import CareersObject
from game.gameConstants import PendingActionType
from typing import Dict, List, Union
import json

class PendingAction(CareersObject):
    '''Encapsulates a pending action for a player. 
        A pending action is some action the player must resolve or lose it.
        See PendingActionType for the types of pending actions.
    '''

    SPECIAL_PROCESSING = Dict[str, Union[str, List[int], int, float, Dict[str, int]]]
    
    def __init__(self, pending_action_type:PendingActionType,  pending_game_square_name:str=None, pending_amount:int=0,pending_dice:int=0, pending_dict:dict={}):
        '''
        Constructor
        '''
        self._pending_action_type = pending_action_type     # 
        self._pending_amount = pending_amount               # value depends on PendingActionType
        self._pending_game_square_name = pending_game_square_name     # name of the GameSquare associated with this pending_action
        self._pending_dice = pending_dice                   # the number of dice to use or 0 if N/A
        self._pending_dict = pending_dict                   # content depends on the game square
        
    
    @property
    def pending_action_type(self) -> PendingActionType:
        return self._pending_action_type
    
    @pending_action_type.setter
    def pending_action_type(self, value:PendingActionType):
        self._pending_action_type = value

    @property  
    def pending_amount(self) -> SPECIAL_PROCESSING:
        return self._pending_amount
    
    @pending_amount.setter
    def pending_amount(self, value:SPECIAL_PROCESSING):
        self._pending_amount = value
        
    @property
    def pending_game_square_name(self) ->str|None:
        return self._pending_game_square_name    # a GameSquare reference
    
    @pending_game_square_name.setter
    def pending_game_square_name(self, value:str):
        self._pending_game_square_name = value
        
    @property
    def pending_dice(self) ->int | List[int]:
        return self._pending_dice
    
    @pending_dice.setter
    def pending_dice(self, value:int | List[int] ):
        '''Set pending dice for the current pending_action.
            This can be an int to represent the number or spaces,
            or the actual dice roll as a List.
        '''
        self._pending_dice = value
        
    @property
    def pending_dict(self)->Dict[str,int]:
        return self._pending_dict
    
    @pending_dict.setter
    def pending_dict(self, value:Dict[str,int]):
        self._pending_dict = value
        
    def clear(self):
        self._pending_action = None
        self._pending_amount = 0
        self._pending_game_square_name = None
        self._pending_dice = 0

    def to_dict(self)->dict:
        pact =  self.pending_action_type.value if self.pending_action_type is not None else "None"
       
        pending_dict = {"pending_action_type":pact, "pending_amount":self.pending_amount, "pending_dice":self.pending_dice}
        if self.pending_game_square_name is not None:
            pending_dict.update({ "pending_game_square_name" : self.pending_game_square_name} )
        return pending_dict
    
    def to_JSON(self):
        return json.dumps(self.to_dict(), indent=2)
    
    