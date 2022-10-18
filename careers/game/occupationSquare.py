'''
Created on Aug 14, 2022

@author: don_bacon
'''
from game.gameSquare import GameSquare, GameSquareClass
from game.player import Player
from game.commandResult import CommandResult
from game.gameUtils import GameUtils
from game.specialProcessing import SpecialProcessingType
from enum import Enum
import json

class OccupationSquareType(Enum):
    DANGER_SQUARE = 'danger_square'
    SHORTCUT_SQUARE = 'shortcut_square'
    ACTION_SQUARE = 'action_square'
    REGULAR_SQUARE = 'regular_square'
    TRAVEL_SQUARE = 'travel_square'


class OccupationSquare(GameSquare):
    '''
    classdocs
    '''
    
    types_list = list(OccupationSquareType)


    def __init__(self, occupation_square_dict, game=None):
        """Create a OccupationSquare instance.
            Arguments:
                occupation_square_dict - the dictionary defining this OccupationSquare. This would be an element of occupationSquares.
                game - a CareersGame instance

        """
        super().__init__("Occupation", name=None, number= occupation_square_dict['number'], \
                         text=occupation_square_dict['text'], special_processing_dict=occupation_square_dict['specialProcessing'], game=game)
        
        self._game_square_dict = occupation_square_dict
        self._game_square_dict["square_class"] =  GameSquareClass.OCCUPATION
        self._stars = occupation_square_dict["stars"]
        self._hearts = occupation_square_dict["hearts"]
        self._experience = occupation_square_dict["experience"]         # the number of Experience cards to collect on this square
        self._opportunities = occupation_square_dict["opportunities"]   # the number of Opportunity cards to collect on this square
        self._square_type = OccupationSquareType[occupation_square_dict.get('type', 'regular_square').upper()]    # square type is optional for OccupationSquare
        self.action_text = occupation_square_dict.get('action_text', None)
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
    def game_square_dict(self):
        return self._game_square_dict
    
    def execute(self, player:Player) -> CommandResult:
        """Executes the actions associated with this occupation square for a given Player
            Returns: CommandResult
        """
        done_flag = True
        message = f'{self.text}'
        next_action = None
        if len(self.action_text) > 0:
            message += f'\n{self.action_text}'
        if self.stars > 0:
            message += f'\n Stars: {str(self.stars)}'
            player.add_stars(self.stars)
        if self.hearts > 0:
            message += f'\n Hearts: {str(self.hearts)}'
            player.add_hearts(self.hearts)
        if self.opportunities > 0:
            for i in range(self.opportunities):
                thecard = self.careersGame.opportunities.draw()
                player.add_opportunity_card(thecard)
        if self.experience > 0:
            for i in range(self.experience):
                thecard = self.careersGame.experience_cards.draw()
                player.add_experience_card(thecard)
        if self.special_processing is not None:
            return self.execute_special_processing(message, player)
            
        result = CommandResult(0, message, done_flag, next_action=next_action)   #  TODO
        return result
    
    def execute_special_processing(self, message, player:Player) ->CommandResult:
        sptype = self.special_processing.processing_type
        dice = self.special_processing.dice
        amount = self.special_processing.amount
        percent = self.special_processing.percent
        next_action = None
        done_flag = True
        if sptype is SpecialProcessingType.BONUS:
            if dice > 0:
                n = GameUtils.roll(dice)
                amount = amount * n
                message += f'\n You rolled a {n}, collect {amount}'
            player.add_cash(amount)
        elif sptype is SpecialProcessingType.SALARY_INCREASE:
            if dice > 0:
                n = GameUtils.roll(dice)
                amount = amount * sum(n)
                message = f'{message}\n You rolled a {n}, salary increase {amount}'
            player.add_to_salary(amount)
        elif sptype is SpecialProcessingType.CASH_LOSS:      # could cause the player into bankruptcy
            payment = self.special_processing.compute_cash_loss(player)
            player.add_cash(-payment)       # this will set the bankrupt pending_action if cash is < 0 as a result
        elif sptype is SpecialProcessingType.FAVORS:
            pass    # TODO
        elif sptype is SpecialProcessingType.SHORTCUT:
            pass    # TODO
        elif sptype is SpecialProcessingType.CASH_LOSS_OR_UNEMPLOYMENT:
            #
            # if the player's cash is < the amount, put them in Unemployment
            # otherwise player needs to choose to pay or go to Unemployment
            #
            if player.cash < amount:
                message += f'\nInsufficient cash to cover amount: {amount}, you will be sent to Unemployment'
                next_action = 'goto unemployment'
                player.pending_action = None
            else:
                player.pending_action = sptype
                player.pending_amount = amount    # always a fixed amount
                done_flag = False
        elif sptype is SpecialProcessingType.TRAVEL_BORDER:
            pass    # TODO
        elif sptype is  SpecialProcessingType.LOSE_NEXT_TURN:
            player.lose_turn = True
        elif sptype is  SpecialProcessingType.EXTRA_TURN:
            player.extra_turn = player.extra_turn + 1
        elif sptype is SpecialProcessingType.SALARY_CUT:
            #
            # if cut is by percent (like half) round up to the nearest $1000
            # So if your $3000 salary is cut in half, it becomes $2000, not $1500
            #
            if amount > 0:
                player.add_to_salary(-amount)
                message += f'Salary cut by {amount}. Your new salary is {player.salary}'
            elif percent > 0:
                cutAmount = player.salary * percent
                cutAmount = 1000 * int(cutAmount / 1000)
                player.add_to_salary(-cutAmount)
                message += f'Salary cut by {cutAmount}. Your new salary is {player.salary}'
        elif sptype is SpecialProcessingType.BACKSTAB:
            ...    # TODO
        elif sptype is SpecialProcessingType.GOTO:
            ...    # TODO
        elif sptype is SpecialProcessingType.FAME_LOSS:
            ...    # TODO
        elif sptype is SpecialProcessingType.HAPPINESS_LOSS:
            ...    # TODO
        return CommandResult(CommandResult.SUCCESS, message, done_flag, next_action=next_action)
    
    def to_JSON(self):
        txt = json.dumps(self.game_square_dict)
        return txt
        
    