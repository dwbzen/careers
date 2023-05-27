'''
Created on Oct 21, 2022

@author: don_bacon
'''

from enum import Enum
from typing import List, Dict
import importlib
import pkgutil
from game import plugins

class PendingActionType(Enum):
    SELECT_DEGREE = "select_degree"
    BUY_EXPERIENCE = "buy_experience"
    BUY_HEARTS = "buy_hearts"
    BUY_STARS = "buy_stars"
    BUY_INSURANCE = "buy_insurance"
    GAMBLE = "gamble"
    STAY_OR_MOVE = "stay_or_move"                           # resolve stay_or_move  stay | move
    TAKE_SHORTCUT = "take_shortcut"
    CASH_LOSS_OR_UNEMPLOYMENT = "cash_loss_or_unemployment" # resolve cash_loss_or_unemployment  pay | unemployment
    CHOOSE_OCCUPATION = "choose_occupation"
    CHOOSE_DESTINATION = "choose_destination"
    BACKSTAB = "backstab"                     # resolve backstab_or_not   <player's initials> | no
    BANKRUPT = "bankrupt"

class SpecialProcessingType(Enum):
    # border squares
    BUY_HEARTS = "buy_hearts"
    BUY_EXPERIENCE = "buy_experience"
    BUY_INSURANCE = "buy_insurance"     # also applies to Opportunity cards
    BUY_STARS = "buy_stars"
    ENTER_COLLEGE = "enter_college"
    ENTER_OCCUPATION = "enter_occupation"
    GAMBLE = "gamble"
    HOLIDAY = "holiday"
    HOSPITAL = "hospital"
    PAYDAY = "payday"
    OPPORTUNITY = "opportunity"
    PAY_TAX = "pay_tax"
    UNEMPLOYMENT = "unemployment"
    
    # occupation squares
    SHORTCUT = "shortcut"
    CASH_LOSS_OR_UNEMPLOYMENT = "cash_loss_or_unemployment"
    GOTO = "goto"
    NEXT_SQUARE = "next_square"
    SALARY_INCREASE = "salary_increase"
    SALARY_CUT = "salary_cut"
    BONUS = "bonus"
    FAVORS = "favors"
    BACKSTAB = "backstab"
    FAME_LOSS = "fame_loss"
    HAPPINESS_LOSS = "happiness_loss"
    
    # common to Occupation and Border squares
    TRAVEL_BORDER = "travel_border"
    CASH_LOSS = "cash_loss"
    EXTRA_TURN = "extra_turn"
    LOSE_NEXT_TURN = "lose_next_turn"
    
class GameParametersType(Enum):  # A.K.A. game mode
    TEST = "test"
    PROD = "prod"
    CUSTOM = "custom"

class GameType(Enum):
    TIMED = "timed"
    POINTS = "points"

class PlayerType(Enum):
    COMPUTER = "computer"
    HUMAN = "human"
    
class GameConstants(object):
    '''
    Define global constants and Enums
    '''
    
    COMMANDS = ['add', 'add_degree', 'advance', 'bankrupt', 'bump', 'buy', 'create', 'done', 'end', 'enter', '_enter',
            'game_status', 'goto', 'info', 'list', 'load', 'location', 'log_message', 'next', 'pay', 'perform', 'quit', 'retire', 
            'roll', 'resolve', 'save', 'saved', 'set', 'start', 'status', 'transfer','turn_history', 'update', 'use', 'use_insurance', 
            'where', 'who']

    def __init__(self, params:Dict):
        '''
        Constructor
        '''
        self._params = params
        
    @property
    def params(self) -> Dict:
        return self._params
    
    @params.setter
    def params(self, value:Dict):
        self._params = value
        
    def get_commands(self) -> List[str]:
        return GameConstants.COMMANDS
    
    @staticmethod
    def get_plugins(edition_name="All") ->List:
        package = plugins
        prefix = package.__name__ + "."
        discovered_plugins = []
        for importer, modname, ispkg in pkgutil.iter_modules(package.__path__, prefix):
            print("Found submodule %s (is a package: %s)" % (modname, ispkg))
            module = __import__(modname, fromlist="dummy")
            print("Imported", module)
            
            if modname.startswith(f'game.plugins.careers_{edition_name}_'):
                discovered_plugins.append(module)

        return discovered_plugins

    