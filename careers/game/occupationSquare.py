'''
Created on Aug 14, 2022

@author: don_bacon
'''
from game.gameSquare import GameSquare, GameSquareClass
from game.player import Player
from game.commandResult import CommandResult
from game.gameUtils import GameUtils
from game.gameConstants import SpecialProcessingType
from enum import Enum
import json, random
from typing import Any

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


    def __init__(self, occupation_square_dict:dict, game:Any=None):
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
            card_list = self.careersGame.opportunities.draw_cards(self.opportunities)
            player.add_opportunity_card(card_list)
        if self.experience > 0:
            card_list = self.careersGame.experience_cards.draw_cards(self.experience)
            player.add_experience_card(card_list)
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
                amount = amount * sum(n)
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
            #
            # collect a randomly selected Opportunity card from the other players
            #
            message = ""
            for aplayer in self.careersGame.game_state.players:
                ncards = len(aplayer.my_opportunity_cards)
                if player.number != aplayer.number and ncards > 0:
                    ind = random.randint(0, ncards-1)    # the index of the card to move to this player
                    thecard = aplayer.my_opportunity_cards[ind]
                    aplayer.remove_opportunity_card(thecard)
                    player.add_opportunity_card(thecard)
                    message += f'Opportunity card "{thecard.text}" moved from player {aplayer.player_initials} to {player.player_initials}\n'
            if len(message) == 0:
                message = "Sadly, no other player has Opportunity to give to you."             

        elif sptype is SpecialProcessingType.SHORTCUT:    # pending action amount is the square# to goto if the shortcut is taken
            next_square = self.special_processing.next_square
            player.set_pending(self.special_processing.pending_action, self, amount=next_square)
            message = f'{player.player_initials} may take a shortcut to square {next_square}'
            
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
            destination = self.special_processing.next_square   # possible destinations: Unemployment and Hospital
            next_action = f'goto {destination}'
            message = f'Go to {destination}'
            player.pending_action = None
            
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
                message += f' Salary cut by {amount}. Your new salary is {player.salary}'
            elif percent > 0:
                cutAmount = player.salary * percent
                cutAmount = 1000 * int(cutAmount / 1000)
                player.add_to_salary(-cutAmount)
                message += f' Salary cut by {cutAmount}. Your new salary is {player.salary}'
                
        elif sptype is SpecialProcessingType.BACKSTAB:
            ...    # TODO
        elif sptype is SpecialProcessingType.GOTO:
            #
            # goto next_square
            #
            message = self.action_text     # could be blank
            next_action = f'goto {self.special_processing.next_square}'
            done_flag = False
            
        elif sptype is SpecialProcessingType.FAME_LOSS:
            ...    # TODO
        elif sptype is SpecialProcessingType.HAPPINESS_LOSS:
            ...    # TODO
        return CommandResult(CommandResult.SUCCESS, message, done_flag, next_action=next_action)
    
    def to_JSON(self):
        txt = json.dumps(self.game_square_dict)
        return txt
        
    