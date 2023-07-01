'''
Created on Aug 12, 2022

@author: don_bacon
'''

from game.careersObject import CareersObject
from game.gameUtils import GameUtils
from game.player import Player
from game.commandResult import CommandResult
from game.gameParameters import GameParameters
from game.gameConstants import PendingActionType, SpecialProcessingType

import json
from typing import Dict, List, Union


class SpecialProcessing(CareersObject):
    """Encapsulates the "specialProcessing" section of a border square or occupation square.
        This is only a model class. The actual processing is done by CareersGameEngine.
    """

    all_types = list(SpecialProcessingType)
    
    SPECIAL_PROCESSING = Dict[str, Union[str, List[int], int, float, Dict[str, int]]]

    def __init__(self, special_processing_dict:SPECIAL_PROCESSING, square_type:str):
        """Constructor
            Arguments:
                special_processing_dict - the JSON specialProcessing section of a border or occupation square as a dictionary
                square_type - "occupation", "border" or "opportunity"
        """
        self._special_processing_dict = special_processing_dict
        #
        # mandatory elements
        #
        self._square_type = square_type     #  "occupation", "border" or "opportunity"
        self._processing_type = SpecialProcessingType[special_processing_dict["type"].upper()]    # must be one of the above types
        #
        # optional elements which are type-dependent
        # an 'amount' can be a numeric type (int or float), a string or a dictionary
        #
        self._amount = 0            # a discrete money amount which may be salary or cash depending on type
        self._amount_dict = None
        self._amount_str = ""
        amt = special_processing_dict.get('amount', 0)    # 'amount' can be a number or a string or a dictionary
        if isinstance(amt, int) or isinstance(amt, float):
            self._amount = amt
        elif isinstance(amt, str):
            self._amount_str = amt
        else:
            self._amount_dict = amt    # how a money amount is calculated
        
        self._dice = special_processing_dict.get('dice', 0)                 # number of dice used to calculate some amount
        self._of = special_processing_dict.get('of', 'cash')                # cash (cash-on-hand) or salary
        self._penalty = special_processing_dict.get('penalty', 0)           # a loss quantity (hearts or stars)
        self._limit = special_processing_dict.get('limit', None)            # a limiting factor, usually "salary" (in 1000s)
        
        # square number to advance to, relative to the overall game layout or occupation
        self._destination_squares:List[int] = special_processing_dict.get('destination_squares', [])
        self._destination_names:List[str] = special_processing_dict.get('destination_names', [])
        next_square = self._destination_squares[0] if  len(self._destination_squares)>0 else None    # default if running in automatic mode (script)
        self._next_square = special_processing_dict.get('next_square', next_square)
        self.next_square_text = special_processing_dict.get('next_square_text', None)

        self._destination = special_processing_dict.get('destinationOccupation', None)  # the name of a destination occupation
        self._percent = special_processing_dict.get('percent', 0.0)                     # a percent amount of salary or cash depending on type
        self._must_roll = special_processing_dict.get('must_roll', [])                  # a list of numbers that must be rolled in order to leave this square
        self._require_doubles = special_processing_dict.get('require_doubles', 0)==1
        self._hearts = special_processing_dict.get('hearts', [])                        # used for holiday type, a 2-element list
        self._tax_table = special_processing_dict.get('taxTable', None)    # format is upper limit : % amount, for example { 3000 : 0.2 } if you make <= 3000/yr, take 20% as tax
        
        pending_action = special_processing_dict.get('pending_action', None) 
        self._pending_action = PendingActionType[pending_action.upper()] if pending_action is not None else None

        self._choices = []
        if special_processing_dict.get('choices',None) is not None:
            self._choices = special_processing_dict.get('choices').split(",")
            
        self._amount_dice = special_processing_dict.get('amount_dice', 0)  # the number of dice to use to determine an amount multiplier
        self._game_parameters = None    # set by GameSquare
    
    @property
    def square_type(self):
        return self._square_type
    
    @property
    def processing_type(self) -> SpecialProcessingType:
        return self._processing_type
    
    @property
    def amount(self):
        return self._amount
    
    @property
    def amount_dict(self):
        return self._amount_dict
    
    @property
    def amount_str(self):
        return self._amount_str
    
    def get_amount(self) -> SPECIAL_PROCESSING:
        '''Returns SPECIAL_PROCESSING amount
        '''
        if self.amount_dict is not None:
            amount = self.amount_dict
        elif len(self.amount_str) > 0:
            amount = self.amount_str
        else:
            amount = self.amount
        return amount
    
    @property
    def destination(self):
        return self._destination
    
    @property
    def dice(self):
        return self._dice
    
    @property
    def limit(self):
        return self._limit
    
    @property
    def next_square(self):
        return self._next_square
    
    @property
    def destination_squares(self) ->List[int]:
        return self._destination_squares
    
    @destination_squares.setter
    def destination_squares(self, values:List[int]):
        self._destination_squares = values
    
    @property
    def destination_names(self) -> List[str]:
        return self._destination_names
    
    @destination_names.setter
    def destination_names(self, values:List[str]):
        self._destination_names = values
    
    @property
    def penalty(self):
        return self._penalty
    
    @property
    def percent(self):
        return self._percent
    
    @property
    def must_roll(self):
        return self._must_roll
    
    @property
    def require_doubles(self):
        return self._require_doubles
    
    @property
    def hearts(self) -> list:
        return self._hearts
    
    @property
    def pending_action(self) ->PendingActionType:
        return self._pending_action
    
    @pending_action.setter
    def pending_action(self, value:PendingActionType):
        self._pending_action = value
    
    @property
    def of(self):
        return self._of
    
    @property
    def tax_table(self):
        return self._tax_table
    
    @property
    def amount_dice(self) -> int:
        return self._amount_dice
    
    @amount_dice.setter
    def amount_dice(self, value:int):
        self._amount_dice = value
        
    @property
    def game_parameters(self) -> GameParameters:
        return self._game_parameters
    
    @game_parameters.setter
    def game_parameters(self, value:GameParameters):
        self._game_parameters = value
        
    @property
    def choices(self) -> List[str]:
        return self._choices
    
    @choices.setter
    def choices(self, values:str):
        self._choices = values.split(",")
    
    def gamble(self, player) -> CommandResult:
        # amount computed from a roll of the dice
        # and could be negative (cash loss) or positive (cash gain)
        # A cash loss is also insurable
        roll = sum(GameUtils.roll(self.amount_dice)) if self.amount_dice > 0 else 1
        amt = self.amount_dict[str(roll)]
        symbol = self.game_parameters.get_param("currency_symbol")
        if isinstance(amt, str):   # fixed amount
            cash_loss = int(amt)
        else:
            cash_loss = roll * amt
        if cash_loss <= 0:
            player.add_point_loss("cast", -cash_loss)
            result = CommandResult(CommandResult.SUCCESS, f'{player.player_initials} rolls a {roll} on a gamble and loses {symbol}{-cash_loss}', True)
        else:
            result = CommandResult(CommandResult.SUCCESS, f'{player.player_initials} rolls a {roll} on a gamble and wins {symbol}{cash_loss}', True)
        player.add_cash(cash_loss)
        return result
    
    def buy_points(self, player, **kwargs):
        '''Process special processing type BUY_HEARTS or BUY_STARS for a given Player
        '''
        result = None
        symbol = self.game_parameters.get_param("currency_symbol")
        if 'choice' in kwargs:    #
            choice = str(kwargs['choice'])
            qty = int(choice)
            if self.amount_dict is not None:    # table of valid quantity + cost
                if choice in self.amount_dict:
                    cost = self.amount_dict[choice]
                    if cost <= player.cash:
                        player.add_points(self.processing_type.value, qty)
                        player.add_points('cash', -cost)
                        result = CommandResult(CommandResult.SUCCESS, f'{player.player_initials} bought {choice} hearts/stars for {symbol}{cost}', True)
                    else:
                        result = result = CommandResult(CommandResult.ERROR, f'Insufficient cash to buy {qty} {self.processing_type.value} ', False)
                    
                else:    # invalid selection
                    result = CommandResult(CommandResult.ERROR, f'{choice} is an invalid choice. Valid choices are {self.amount_dict}', False)
            else:           # a fixed amount with a possible penalty if quantity is 0
                cost = self.amount * qty
                what = kwargs.get('what','')
                if cost <= player.cash:
                    if self.limit is not None and self.limit == 'salary' :
                        if cost <= player.salary:
                            if qty == 0 and self.penalty > 0:
                                player.add_points(self.processing_type.value, -self.penalty)
                                result = CommandResult(CommandResult.SUCCESS, f'You lose {self.penalty} {what} for "just looking"', True)
                            else:
                                player.add_points(self.processing_type.value, qty)
                                player.add_points('cash', -cost)
                                result = CommandResult(CommandResult.SUCCESS, f'You bought {qty} {what} for {symbol}{cost}', True)
                        else:
                            result = CommandResult(CommandResult.ERROR, f'You can only buy up to {int(player.salary/1000)} here. ', False)
                else:
                    result = CommandResult(CommandResult.ERROR, f'Insufficient cash to buy {qty} {self.processing_type.value} ', False)
        return result
            
    def compute_cash_loss(self, player:Player) -> int:
        """Compute the cash loss for this specialProcessing given cash and salary amounts.
             Cash loss can be a fixed amount or a percentage of a player's salary or cash on hand
            It's possible the loss causes the player to have negative cash in which case they
            will not be able to move without resolving by either borrowing the money from 
            another player or declaring bankruptcy
        """
        cash_loss = 0
        player_salary = player.salary
        player_cash = player.cash
        player_net_worth = player_cash + player.savings - player.get_total_loans()
        if self.processing_type is SpecialProcessingType.PAY_TAX:
            # compute tax amount from tax table as a % of salary
            for k in self.tax_table.keys():
                amt = int(k)
                if player_salary <= amt:
                    cash_loss = int(self.tax_table[k] * player_salary)    # truncate the amount
                    
        elif self.processing_type is SpecialProcessingType.CASH_LOSS:
            if self.of=='net_worth':
                cash_loss = self._compute_amount(player_net_worth)
            else:    
                cash_loss = self._compute_amount(player_cash) if self.of=='cash' else self._compute_amount(player_salary)
            player.add_point_loss("cash", cash_loss)    # cash loss is covered by insurance
            
        elif  self.processing_type is SpecialProcessingType.CASH_LOSS_OR_UNEMPLOYMENT.value:
            cash_loss = self._compute_amount(player_cash) if self.of=='cash' else self._compute_amount(player_salary)
            player.pending_amount = cash_loss
            
        elif self.processing_type is SpecialProcessingType.UNEMPLOYMENT or self.processing_type is SpecialProcessingType.HOSPITAL:
            cash_loss =  self._compute_amount(player_cash) if self.of=='cash' else self._compute_amount(player_salary)
        
        else:   # future expansion
            pass
        
        return cash_loss
    
    def compute_point_loss(self, of_what:str, fame_points:int, happiness_points:int):
        """Computes the loss of fame or happiness points
            Arguments:
                what - 'happiness' or 'fame'
                famePoints - player's fame points (Stars)
                happinessPoints - 
        """
        point_loss = self._compute_amount(fame_points) if of_what=='fame' else self._compute_amount(happiness_points)
        
        return point_loss
    
    def _compute_amount(self, original_amount:int) -> int:
        theAmount = 0
        if self.amount != 0:
            if self.dice > 0:
                roll = GameUtils.roll(self.dice)
                theAmount = sum(roll) * self.amount
            else:
                theAmount = self.amount
        elif self.percent != 0.0:
            if self.dice > 0:
                roll = GameUtils.roll(self.dice)
                theAmount = int(sum(roll) * self.percent * original_amount)
            else:
                theAmount = int(self.percent * original_amount)
            if self.of == 'salary':     # round up to nearest thousand $ (or pounds)
                theAmount = 1000 * int(theAmount / 1000)
        
        return theAmount
    
    def __str__(self):
        return str(self._special_processing_dict)
    
    def to_JSON(self):
        return json.dump(self._special_processing_dict, indent=2)
