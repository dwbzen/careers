'''
Created on Oct 21, 2022

@author: don_bacon
'''

from enum import Enum
from typing import List, Dict
import random
import pkgutil
from game.environment import Environment

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
    TRAVEL_CHOICE = "travel_choice"    # choose next travel square, travel class depends on the edition
    BIDIRECTIONAL_TRAVEL_CHOICE = "bidirectional_travel_choice"

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
    CASH_LOSS_AND_UNEMPLOYMENT = "cash_loss_and_unemployment"
    GOTO = "goto"
    NEXT_SQUARE = "next_square"
    SALARY_INCREASE = "salary_increase"
    SALARY_CUT = "salary_cut"
    BONUS = "bonus"
    BONUS_ALL = "bonus_all"    # applies to all players who have completed the Occupation
    FAVORS = "favors"
    BACKSTAB = "backstab"
    FAME_LOSS = "fame_loss"
    HAPPINESS_LOSS = "happiness_loss"
    WORMHOLE = "wormhole"
    
    # common to Occupation and Border squares
    TRAVEL_BORDER = "travel_border"
    TRAVEL_CHOICE = "travel_choice"    # go to nearest airline or rail station, also a PendingActionType to specify the choice
    TRAVEL_OCCUPATION = "travel_occupation"
    BIDIRECTIONAL_TRAVEL_CHOICE = "bidirectional_travel_choice"     # forward of backward to travel square choice
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

class BorderSquareType(str, Enum):
    # CORNER_SQUARE is deprecated, replaced by the specific type of corner square: Hospital, Unemployment, Holiday
    CORNER_SQUARE = 'corner_square'
    PAYDAY_SQUARE = 'payday_square'
    HOSPITAL_SQUARE = 'hospital_square'
    UNEMPLOYMENT_SQUARE = 'unemployment_square'
    HOLIDAY_SQUARE = 'holiday_square'     # Holiday, Spring Break etc.
    OPPORTUNITY_SQUARE = 'opportunity_square'
    DANGER_SQUARE = 'danger_square'
    TRAVEL_SQUARE = 'travel_square'
    OCCUPATION_ENTRANCE_SQUARE = 'occupation_entrance_square'
    ACTION_SQUARE = 'action_square'

class OccupationSquareType(Enum):
    ACTION_SQUARE = 'action_square'
    DANGER_SQUARE = 'danger_square'
    DANGER_WORMHOLE_SQUARE = 'danger_wormhole_square'
    OCCUPATION_SQUARE = 'occupation_square'
    SHORTCUT_SQUARE = 'shortcut_square'
    OPPORTUNITY_SQUARE = 'opportunity_square'
    TRAVEL_SQUARE = 'travel_square'

class TravelClass(str, Enum):
    RAIL = 'rail'
    UNDERGROUND = 'underground'    # UK edition
    SUBWAY = 'subway'              # US editions
    AIR = 'air'                    # airports
    
class PlayerType(Enum):
    COMPUTER = "computer"
    HUMAN = "human"

class StrategyLevel(Enum):
    DUMB = 0        # just "roll"
    BASIC = 1       # pick a command at random
    SMART = 2       # basic strategy
    GENIUS = 3      # use trained model
    
class GameConstants(object):
    '''
    Define global constants and Enums
    '''
    
    COMMANDS = ['add', 'add_degree', 'advance', 'bankrupt', 'bump', 'buy', 'create', 'done', 'end', 'enter', '_enter',
            'game_status', 'goto', 'help', 'info', 'list', 'load', 'location', 'log_message', 'lose_turn', 'need', 'next', 'pay', 'perform', 'quit', 'retire', 
            'roll', 'resolve', 'save', 'saved', 'set', 'start', 'status', 'take_turn', 'transfer', 'turn_history', 
            'update', 'use', 'use_insurance', 'where', 'who']
    
    CURRENCY_SYMBOL = "$"    # default, set by CareersGameEngine from gameParameters JSON file
    
    #
    # point_icon definitions initially defaulted, can be updated with load_point_icons()
    #
    HEART = "Heart"
    HAPPINESS = "Happiness"
    STAR = "Star"
    FAME = "Fame"
    
    HEART_LC = "heart"
    HAPPINESS_LC = "happiness"
    STAR_LC = "star"
    FAME_LC = "fame"

    CORNER_SQUARE_TYPES = [BorderSquareType.PAYDAY_SQUARE, \
                           BorderSquareType.HOSPITAL_SQUARE,\
                           BorderSquareType.UNEMPLOYMENT_SQUARE,\
                           BorderSquareType.HOLIDAY_SQUARE]
    
    #
    # This structure is built in CareersGame load_occupations() -> Occupation._create_occupation_squares
    #
    wormholes:List[Dict] = []
    
    def __init__(self, params:Dict={} ):
        '''
        Constructor
        '''
        self._params = params

        self._wormhole_ref:List[Dict] = []
        
    @property
    def params(self) -> Dict:
        return self._params
    
    @params.setter
    def params(self, value:Dict):
        self._params = value
        
    def get_commands(self) -> List[str]:
        return GameConstants.COMMANDS
    
    @staticmethod
    def get_currency_symbol()->str:
        return GameConstants.CURRENCY_SYMBOL
    
    @staticmethod
    def set_currency_symbol(value:str):
        GameConstants.CURRENCY_SYMBOL = value
        
    @staticmethod
    def get_wormholes() ->List[Dict]:
        return GameConstants.wormholes
    
    @staticmethod
    def add_wormhole(wormhole:Dict):
        """Adds a wormhole to the wormholes list
            wormhole Dict format is { "occupation_name" : <occupation_name>, "number": <wormhole_square number> }
            for example  {"occupation_name" : "VentureCapitalist" , "number" : 7}
        """
        GameConstants.wormholes.append(wormhole)
    
    @staticmethod
    def pick_random_wormhole() -> Dict:
        """Pick and return a wormhole at random from GameConstants.wormholes.
            If there are no wormholes, return an empty Dict {}
        """
        wn = len(GameConstants.wormholes)
        return GameConstants.wormholes[random.randrange(len(GameConstants.wormholes))] if wn > 0 else {}
        
    @staticmethod
    def get_plugins(edition_name="All", apath=None) ->List[Dict]:
        """Discover and return game plugins.
            This searches the game.plugins package for modules matching the provided edition_name.
            Arguments:
                edition_name - "All" for all editions, or a specific edition name such as "Hi-Tech"
                apath - the search path. If not provided it defaults to the Environment game_path/plugins,
                        for example "C:/Compile/careers/game/plugins"
            Returns:
                A List[Dict] where each Dict has the keys "name" (the module name, for example 'careers.game.plugins.careers_All_Randomizer'
                and "module" (the python module object)
            If an specific edition is requested, any _All_ modules are also returned, since they apply to all editions.
        """
        path = f'{Environment.get_environment().game_path}/plugins' if apath is None else apath
        prefix = "careers.game.plugins"
        discovered_plugins = []
        for importer, modname, ispkg in pkgutil.iter_modules([path], f"{prefix}."):
            # print("Found submodule '%s' (is a package: %s)" % (modname, ispkg))
            module = __import__(modname, fromlist="dummy")
            # print("Imported", module)
            # sample modnames:  'careers.game.plugins.careers_All_Randomizer', 'careers.game.plugins.careers_HiTech_Rules' 
            if "_All_" in modname or edition_name in modname:
                mdict = {"name":modname, "module":module}
                discovered_plugins.append(mdict)

        return discovered_plugins

    @staticmethod
    def load_point_icons(point_icons:Dict):
        if point_icons is not None and len(point_icons) > 0:
            GameConstants.HEART = point_icons["Heart"]
            GameConstants.HAPPINESS = point_icons["Happiness"]
            GameConstants.STAR = point_icons["Star"]
            GameConstants.FAME = point_icons["Fame"]
            
            GameConstants.HEART_LC = point_icons["heart"]
            GameConstants.HAPPINESS_LC = point_icons["happiness"]
            GameConstants.STAR_LC = point_icons["star"]
            GameConstants.FAME_LC = point_icons["fame"]
        # else use the default vales

    