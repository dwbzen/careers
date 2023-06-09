'''
Created on Nov 25, 2022

@author: don_bacon
'''
from game.careersObject import CareersObject
from game.pendingAction import PendingAction
from game.gameConstants import PendingActionType
from typing import List
import json

class PendingActions(CareersObject):
    '''
    Represents a collection of PendingAction
    '''

    _pending_action_types = [x.value for x in list(PendingActionType)]

    def __init__(self, pendingAction:PendingAction=None):
        '''
        Constructor
        '''
        self._pending_actions:List[PendingAction] = []
        if pendingAction is not None:
            self._pending_actions.append(pendingAction)
    
    def size(self)->int:
        return len(self._pending_actions)
    
    def add(self, pendingAction:PendingAction)->bool:
        """Adds a PendingAction to the pending actions list.
            Note that PendingActions may have at most 1 element of
            a given PendingActionType.
            Returns:
                True if added,
                False if not added because that PendingAction (of a given type) is already in the list
        """
        added = False
        if self.index_of(pendingAction.pending_action_type) < 0:
            self._pending_actions.append(pendingAction)
            added = True
        return added
        
    
    def index_of(self, pending_action_type:PendingActionType|str)->int:
        """Finds the index of the PendingAction with a given PendingActionType
            Arguments:
                pending_action_type - a PendingActionType or a str value in PendingActionType
            Returns:
                if found, the index of the item, >0 and < size()
                -1 if not found
        """
        ind = 0
        pat = None
        if isinstance(pending_action_type, str):
            if pending_action_type in PendingActions._pending_action_types:
                pat = PendingActionType[pending_action_type.upper()]

        else:
            pat = pending_action_type
            
        for pa in self._pending_actions:
            if pa.pending_action_type is pat:
                return ind
            else:
                ind+=1
        return -1
    
    def get_pending_action(self, pending_action_type:PendingActionType|str, remove:bool=False) -> PendingAction:
        """Gets the PendingAction of a given type.
            Arguments:
                pending_action_type - a PendingActionType or a str value in PendingActionType
                remove - if True pop the pending_actions list at the specified index, removing it from the list.
                        If false, return the PendingAction without removal.
                        Default is False
            Returns:
                if found, the PendingAction, None if not found
        """
        pending_action = None
        index = self.index_of(pending_action_type)
        if index >= 0:
            if remove:
                pending_action = self._pending_actions.pop(index)
            else:
                pending_action = self._pending_actions[index]
        return pending_action
    
    def get(self, index:int=-1, remove:bool=False) -> PendingAction:
        """Gets the PendingAction at the specified index
            Arguments:
                index - the index to get. Must satisfy -1 <= index < self.size()
                remove - if True pop the pending_actions list at the specified index, removing it from the list.
                        If false, return the PendingAction without removal.
                        Default is False
        """
        assert(index >= -1 and index < self.size())
        if remove:
            return self._pending_actions.pop(index)
        else:
            return self._pending_actions[index]
        
    def remove_all_but(self, pending_action_type:PendingActionType):
        """Removes all PendingAction from the list except those having a specified PendingActionType.
            Arguments:
                pendingActionType - the PendingActionType to keep. If None, all are removed, emptying the list.
        """
        if pending_action_type is None:
            self._pending_actions.clear()
        else:
            pactions = []
            for pa in self._pending_actions:
                if pa.pending_action_type is not pending_action_type:
                    pactions.append(pa)
            self._pending_actions = pactions
                      
    def find(self, pendingActionType:PendingActionType, remove:bool=False) -> PendingAction|None:
        """Gets the PendingAction of a given type and removes it from the list
            Arguments:
                pendingActionType - the PendingActionType to find
                remove - if True pop the pending_actions list at the specified index, removing it from the list.
                        If false, return the PendingAction without removal.
                        Default is False
            Returns:
                The requested PendingAction if found, None otherwise
        """
        pa = None
        index = self.index_of(pendingActionType)
        if index >= 0:
            if remove:
                pa = self._pending_actions.pop(index)
            else:
                pa = self._pending_actions[index]
        return pa

    def remove(self, pendingActionType:PendingActionType)  -> PendingAction|None:
        return(self.find(pendingActionType))

    @property
    def pending_actions(self)->List[PendingAction]:
        return self._pending_actions
    
    @pending_actions.setter
    def pending_actions(self, value):
        self._pending_actions = value
    
    def get_all(self)->List[PendingAction]:
        return self._pending_actions
    
    def to_dict(self):
        pl = []
        for pa in self._pending_actions:
            pl.append(pa.to_dict())
        pending_dict = {"pending_actions":pl}
        return pending_dict
    
    def to_JSON(self):
        return json.dumps(self.to_dict(), indent=2)
    
if __name__ == '__main__':
    print(PendingActions.__doc__)
        
        