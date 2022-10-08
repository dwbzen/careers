'''
Created on Aug 12, 2022

@author: don_bacon
'''

from game.gameSquare import GameSquare
from game.player import Player
from game.commandResult import CommandResult
from typing import Any, List
import json

class BorderSquare(GameSquare):
    """Encapsulates a Careers game border (non-occupation) square.
    Border squares are numbered consecutively starting with 0 (Payday by convention).
    They also have a name which may not be unique. For example, there are 12 squares named "Opportunity"
    The border square "type" is enumerated in the gameLayout JSON as "types_list
    """

    types_list = ["corner_square", "opportunity_square", "danger_square", "travel_square", "occupation_entrance_square", "action_square"]


    def __init__(self, border_square_dict, game=None):
        """Create a BorderSquare instance.
            Arguments:
                border_square_dict - the dictionary defining this BorderSquare. This would be an element of the game layout.
                game - a CareersGame instance

        """
        super().__init__("Border", name=border_square_dict['name'], number= border_square_dict['number'], \
                         text=border_square_dict['text'], special_processing_dict=border_square_dict['specialProcessing'], game=game)
        
        self._game_square_dict = border_square_dict
        self._game_square_dict["square_class"] = "Border"
        self._square_type = border_square_dict['type']
        self.action_text = border_square_dict.get('action_text', None)

    @property
    def game_square_dict(self):
        return self._game_square_dict
    
    def execute(self, player:Player) -> CommandResult:
        """Execute the actions associated with landing on this BorderSquare. Overrides GameSquare.execute().
            Assumes the Player's current location is this BorderSquare.
            Arguments:
                player - current Player
            Returns: CommandResult
        """
        careersGame = self._careersGame
        if self.name == 'Opportunity':
            deck = careersGame.opportunities
            card = deck.draw()
            player.my_opportunity_cards.append(card)
            return CommandResult(CommandResult.SUCCESS, f'Added Opportunity: {str(card)}', True)
        
        elif self.square_type == 'travel_square':
            #
            # advance to the next travel_square and roll again
            # 
            #
            next_square_number = self._careersGame.find_next_border_square(self.number, 'travel_square')
            game_square = careersGame.game_board.get_square(next_square_number)
            next_action = f'goto {next_square_number};roll'    # player.board_location set by 'goto' command

            result = CommandResult(CommandResult.SUCCESS, f'Advance to square {next_square_number}, {game_square.name} and roll again', False)
            result.next_action = next_action
            #result.board_location = player.board_location
            return result
        
        elif self.square_type == 'occupation_entrance_square':
            #
            # can enter if landed here using an Opportunity, else turn is over
            #
            if player.opportunity_card is not None:
                if player.opportunity_card.opportunity_type  == 'occupation' and player.opportunity_card.destination == self.name:
                    next_action = f'enter {self.name}'
                    result = CommandResult(CommandResult.SUCCESS, f'Entering {self.name}', False, next_action=next_action)
            else:
                result = CommandResult(CommandResult.SUCCESS, "", True)
            return result
        elif self.square_type == 'action_square':
            sp_type = self.special_processing.processing_type       # independent of the name of the Square
            player.pending_action = sp_type                         # Set the pending_action 
            message = f'{self.text}\n{self.action_text}'
            if sp_type == 'buyHearts':    # Tech Convention
                return CommandResult(CommandResult.NEED_PLAYER_CHOICE, message, False)   # player needs to execute a 'buy hearts'
            elif sp_type == 'buyExperience':
                return CommandResult(CommandResult.NEED_PLAYER_CHOICE, message, False)   # player needs to execute a 'buy experience' 
            elif sp_type == 'buyInsurance':
                return CommandResult(CommandResult.NEED_PLAYER_CHOICE, message, False)   # player needs to buy insurance
            elif sp_type == 'gamble':               # Roll 2 dice to gamble
                return CommandResult(CommandResult.NEED_PLAYER_CHOICE, message, False)   # player needs to indicate they intend to Gamble, then roll
            else:
                #
                # return the JSON dumps of this square as landing here requires a choice by the player
                # to buy hearts, stars, experience cards or to gamble
                # The UI will send back the appropriate command if the player wants to execute the square
                # this will include the choice amount.
                #
                message = self.to_JSON()
                return CommandResult(CommandResult.NEED_PLAYER_CHOICE, message, False)
        elif self.square_type == 'corner_square':
                # check special processing type because corner square names are edition-dependent, specialProcessing type is independent of the edition
    
                sp_type = self.special_processing.processing_type
                if sp_type == "unemployment":
                    player.is_unemployed = True
                    self.update_board_location(player)
                    result = CommandResult(CommandResult.SUCCESS, f'Player {player.player_initials}: {self.action_text}', True)
                elif sp_type == "hospital":
                    player.is_sick = True
                    self.update_board_location(player)
                    result = CommandResult(CommandResult.SUCCESS, f'Player {player.player_initials}: {self.action_text}', True)                  
                elif sp_type == "payday":
                    salary = player.salary
                    # if I am on Payday I get double salary
                    # don't update the player's board_location 
                    how = "passed" 
                    if player.board_location.border_square_number == 0: 
                        salary += salary
                        how = "landed on"
                    player.cash += salary
                    player.laps += 1
                    result = CommandResult(CommandResult.SUCCESS, f'Player {player.player_initials} {how} {self.name}\n{self.action_text}', True)
                elif sp_type == "holiday":    # a.k.a. Spring Break, Holiday
                    # the number of hearts you get is configured in the specialProcessing section 
                    nhearts = self.special_processing.hearts[0] if player.on_holiday else self.special_processing.hearts[1]
                    player.on_holiday = True
                    player.add_hearts(nhearts)
                    self.update_board_location(player)
                    result = CommandResult(CommandResult.SUCCESS, f'Player {player.player_initials} {self.action_text}\n collect {nhearts} hearts', True)
                    
                return result
        elif self.square_type == 'danger_square':   # IncomeTax, DonateNow, CarPayment, PayRent, ShoppingSpree, DivorceCourt
            sp_type = self.special_processing.processing_type    # special processing type independent of the square name
            payment = self.special_processing.compute_cash_loss(player.salary, player.cash)
            player.add_cash(-payment)       # this will set the bankrupt pending_action if cash is < 0 as a result
            result =  CommandResult(CommandResult.SUCCESS, f'{self.action_text}\n Player {player.player_initials}  pays {payment}, remaining cash: {player.cash}', player.cash < 0)
        else:
            result = CommandResult(CommandResult.SUCCESS, f'{self.square_type} {self.name} execute not yet implemented', False)   #  TODO
        return result
    
    def execute_special_processing(self, player:Player, dice:List[int]=None):
        """Invokes the specialProcessing section of this border square for a player.
            Arguments:
                player - the current Player (who landed on this border square)
                dice - optional, the player's dice roll
            Returns: CommandResult
            
            This method is called as exit processing for a square or as needed, whereas execute() is called when a player lands on a border square.
            
            TODO - finish this, for now return SUCCESS
        """
        sp_type = self.special_processing.processing_type
        if sp_type == 'unemployment' or sp_type == 'hospital':
            #
            # check the roll against "must_roll" and "require_doubles"
            #
            num_spaces = sum(dice)
            can_roll =  num_spaces in self.special_processing.must_roll or (self.special_processing.require_doubles and dice[0] == dice[1])
            if can_roll:
                result = CommandResult(CommandResult.SUCCESS, f'Player can leave {self.name}', True)
            else:
                result = CommandResult(CommandResult.EXECUTE_NEXT, f'Player rolled {dice} and must remain in {self.name}', True, next_action="next")
        else:
            result = CommandResult(CommandResult.SUCCESS, f'{self.square_type} {self.name} execute_special_processing not yet implemented', False)
        
        return result
    
    def update_board_location(self, player:Player):
        player.board_location.border_square_number = self.number
        player.board_location.border_square_name = self.name
        player.board_location.occupation_name = None     
        
    def to_JSON(self):
        return json.dumps(self.game_square_dict)


    