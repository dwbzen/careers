'''
Created on Aug 12, 2022

@author: don_bacon
'''

from game.gameSquare import GameSquare
from game.player import Player
from game.commandResult import CommandResult
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
        self._square_type = border_square_dict['type']
        if "action_text" in border_square_dict:
            self.action_text = border_square_dict['action_text']
        
        
    @property
    def square_type(self):
        return self._square_type
    
    @square_type.setter
    def square_type(self, value):
        self._square_type = value
        
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
                if player.opportunity_card.opportunity_type  == 'occupation' and player.opportunity_card.name == self.name:
                    next_action = f'enter {self.name}'
                    result = CommandResult(CommandResult.SUCCESS, f'Entering {self.name}', False, next_action=next_action)
            else:
                result = CommandResult(CommandResult.SUCCESS, "", True)
            return result
        elif self.square_type == 'action_square':
            if self.name == 'BuyInsurance':         # nothing to do, buy_insurance is a separate command
                return CommandResult(CommandResult.NEED_PLAYER_CHOICE, "", False)
            else:
                #
                # return the JSON dumps of this square as landing here requires a choice by the player
                # to buy hearts, stars, experience cards or to gamble
                # The UI will send back the appropriate command if the player wants to execute the square
                # this will include the choice amount.
                #
                message = self.to_JSON()
                return CommandResult(CommandResult.NEED_PLAYER_CHOICE, message, False)
        else:
            pass
        
        result = CommandResult(CommandResult.SUCCESS, f'execute not yet implemented for {self.square_type} {self.name} ', False)   #  TODO
        return result
        
    def to_JSON(self):
        return json.dumps(self.game_square_dict)


    