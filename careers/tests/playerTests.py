'''
Created on Dec 1, 2022

@author: don_bacon
'''

from game.pendingActions import PendingActions
from game.pendingAction import PendingAction
from game.gameConstants import PendingActionType
import unittest

if __name__ == '__main__':
    pending_actions = PendingActions()
    print(pending_actions.to_JSON())
    pa_buy_hearts = PendingAction(PendingActionType.BUY_HEARTS, pending_amount=1)
    pa_buy_insurance = PendingAction(PendingActionType.BUY_INSURANCE)
    pa_select_degree = PendingAction(PendingActionType.SELECT_DEGREE)
    pa_stay_or_move = PendingAction(PendingActionType.STAY_OR_MOVE, pending_dice=1)

    print(pending_actions.add(pa_buy_hearts))
    print(pending_actions.add(pa_buy_insurance))
    print(pending_actions.add(pa_stay_or_move))
    print(pending_actions.add(pa_select_degree))
    print(f'size: {pending_actions.size()}')
    print(pending_actions.to_JSON())
    print()
    
    pa = pending_actions.get_pending_action(PendingActionType.STAY_OR_MOVE)    # get without removing from the list
    print(pa.to_JSON())
    print(f'size: {pending_actions.size()}\n')
    pa.pending_dice = 2
    
    #
    pa = pending_actions.get()    # get the last one added SELECT_DEGREE
    print(pa.to_JSON())
    print(f'size: {pending_actions.size()}\n')   
    
    pa = pending_actions.get(0)   # get the first one BUY_HEARTS
    print(pa.to_JSON())
    print(f'size: {pending_actions.size()}\n')
    
    pa = pending_actions.get(1)   # get the 2nd one STAY_OR_MOVE
    print(pa.to_JSON())
    print(f'size: {pending_actions.size()}\n')
    
    # add one that's already there
    print(pending_actions.add(pa_buy_insurance))
    print(f'size: {pending_actions.size()}')
    

    