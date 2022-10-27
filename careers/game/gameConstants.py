'''
Created on Oct 21, 2022

@author: dwbze
'''

from enum import Enum


class PendingAction(Enum):
    SELECT_DEGREE = "select_degree"
    BUY_EXPERIENCE = "buy_experience"
    BUY_HEARTS = "buy_hearts"
    BUY_STARS = "buy_stars"
    BUY_INSURANCE = "buy_insurance"
    GAMBLE = "gamble"
    STAY_OR_MOVE = "stay_or_move"
    TAKE_SHORTCUT = "take_shortcut"
    CASH_LOSS_OR_UNEMPLOYMENT = "cash_loss_or_unemployment"

class GameConstants(object):
    '''
    classdocs
    '''
    
    COMMANDS = ['add', 'bankrupt', 'bump', 'buy', 'create', 'done', 'end', 'enter', 
            'game_status', 'goto', 'info', 'list', 'load', 'next', 'pay', 'perform', 'quit', 'retire', 
            'roll', 'resolve', 'save', 'saved', 'start', 'status', 'transfer', 'use', 'use_insurance', 
            'where', 'who']

    def __init__(self, params:dict):
        '''
        Constructor
        '''
        self._params = params
        
    @property
    def params(self) -> dict:
        return self._params
    
    @params.setter
    def params(self, value:dict):
        self._params = value