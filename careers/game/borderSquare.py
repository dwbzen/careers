'''
Created on Aug 12, 2022

@author: don_bacon
'''

from game.gameSquare import GameSquare, GameSquareClass
from game.player import Player
from game.commandResult import CommandResult
from game.gameConstants import SpecialProcessingType, GameConstants
from game.opportunityCard import OpportunityType
from game.gameConstants import BorderSquareType, TravelClass

from typing import  List
import json

class BorderSquare(GameSquare):
    """Encapsulates a Careers game border (non-occupation) square.
    Border squares are numbered consecutively starting with 0 (Payday by convention).
    They also have a name which may not be unique. For example, there are 12 squares named "Opportunity"
    The border square "type" is enumerated in the gameLayout JSON as "types_list
    
    Note: the square name for Hospital and Unemployment must the same across all editions.
    """

    types_list = list(BorderSquareType)


    def __init__(self, border_square_dict:dict, game=None):
        """Create a BorderSquare instance.
            Arguments:
                border_square_dict - the dictionary defining this BorderSquare. This would be an element of the game layout.
                game - a CareersGame instance

        """
        super().__init__("Border", name=border_square_dict['name'], number= border_square_dict['number'], \
                         text=border_square_dict['text'], special_processing_dict=border_square_dict['specialProcessing'], game=game)
        
        self._game_square_dict = border_square_dict
        self._game_square_dict["square_class"] = GameSquareClass.BORDER
        self._square_type = BorderSquareType[border_square_dict['type'].upper()]
        action_text = border_square_dict.get('action_text', None)
        if action_text is not None:
            action_text = action_text.replace("<HEART>", GameConstants.HEART.title())
            action_text = action_text.replace("<STAR>", GameConstants.STAR.title())
            action_text = action_text.replace("<HAPPINESS>", GameConstants.HAPPINESS.title())
            self.action_text = action_text.replace("<FAME>", GameConstants.FAME.title())
        else:
            self.action_text = None
        self._help_text = border_square_dict.get('help_text', None)
        self._travel_class = None
        if border_square_dict.get('travel_class', None) is not None:
            self._travel_class = TravelClass[border_square_dict['travel_class'].upper()]

    @property
    def game_square_dict(self):
        return self._game_square_dict
    
    @property
    def travel_class(self) ->TravelClass | None:
        return self._travel_class
    
    @property
    def square_type(self) -> BorderSquareType:
        return self._square_type
    
    def execute(self, player:Player, dice:List[int]=None) -> CommandResult:
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
        
        match(self.square_type):
            
            case BorderSquareType.TRAVEL_SQUARE:
                #
                # advance to the next travel_square and roll again
                # If this is a travel_choice, set the pending_action to TRAVEL_CHOICE
                if self.special_processing.processing_type is SpecialProcessingType.TRAVEL_CHOICE:
                    pending_action_type = self.special_processing.pending_action         # PendingActionType
                    destination_names = self.special_processing.destination_names        # List[str] len=2
                    message = f'{self.text}. {self.action_text} {destination_names}'
                    player.add_pending_action(pending_action_type, game_square_name=self.name)
                    result = CommandResult(CommandResult.NEED_PLAYER_CHOICE, message, False)   # player needs to pick the destination travel_square
                else:
                    next_square_number, game_square = self._careersGame.find_next_border_square(self.number, BorderSquareType.TRAVEL_SQUARE)
                    next_action = f'goto {next_square_number};roll'    # player.board_location set by 'goto' command
                    result = CommandResult(CommandResult.SUCCESS, f'Advance to square {next_square_number}, {game_square.name} and roll again', False)
                    result.next_action = next_action
                    
                return result
        
            case BorderSquareType.OCCUPATION_ENTRANCE_SQUARE:
                #
                # can enter if landed here using an Opportunity, else turn is over
                #
                if player.opportunity_card is not None:
                    if player.opportunity_card.opportunity_type  is OpportunityType.OCCUPATION and player.opportunity_card.destination == self.name:
                        next_action = f'enter {self.name}'
                        result = CommandResult(CommandResult.SUCCESS, f'Entering {self.name}', False, next_action=next_action)
                    else:
                        result = CommandResult.successfull_result()
                else:
                    result = CommandResult.successfull_result()
                return result
        
            case BorderSquareType.ACTION_SQUARE:
                sp_type = self.special_processing.processing_type       # independent of the name of the Square
                pending_action = self.special_processing.pending_action         # PendingActionType
                message = f'{self.text}\n{self.action_text}'
                match(sp_type):
                    case SpecialProcessingType.BUY_HEARTS | SpecialProcessingType.BUY_STARS:
                        player.add_pending_action(pending_action, game_square_name=self.name, amount=self.special_processing.get_amount())
                        return CommandResult(CommandResult.NEED_PLAYER_CHOICE, message, False)   # player needs to execute a 'buy hearts' or 'buy stars'
                
                    case SpecialProcessingType.BUY_EXPERIENCE:
                        player.add_pending_action(pending_action, game_square_name=self.name, amount=self.special_processing.get_amount())
                        return CommandResult(CommandResult.NEED_PLAYER_CHOICE, message, False)   # player needs to execute a 'buy experience' 
                
                    case SpecialProcessingType.BUY_INSURANCE:
                        player.add_pending_action(pending_action, game_square_name=self.name, amount=self.special_processing.get_amount())
                        return CommandResult(CommandResult.NEED_PLAYER_CHOICE, message, False)   # player needs to buy insurance
                
                    case SpecialProcessingType.GAMBLE: 
                        player.add_pending_action(pending_action, game_square_name=self.name, dice=self.special_processing.dice)  # Roll 2 dice to gamble
                        return CommandResult(CommandResult.NEED_PLAYER_CHOICE, message, False)   # player needs to indicate they intend to Gamble, then roll
                
                    case _:
                        # If you get this far, the sp_type is invalid or unsupported
                        message = f'Invalid SpecialProcessingType {sp_type} for {message}'
                        return CommandResult(CommandResult.ERROR, message, False)
            
            case BorderSquareType.CORNER_SQUARE:
                # check special processing type because corner square names are edition-dependent, specialProcessing type is independent of the edition
                special_processing = self.special_processing
                sp_type = special_processing.processing_type

                match(sp_type):
                    case SpecialProcessingType.UNEMPLOYMENT:
                        player.is_unemployed = True
                        self.update_board_location(player)
                        player.can_use_opportunity = False
                        player.clear_pending()
                        result = CommandResult(CommandResult.SUCCESS, f'Player {player.player_initials}: {self.action_text}', True)
                    
                    case SpecialProcessingType.HOSPITAL:
                        player.is_sick = True
                        self.update_board_location(player)
                        player.can_use_opportunity = False
                        player.clear_pending()
                        result = CommandResult(CommandResult.SUCCESS, f'Player {player.player_initials}: {self.action_text}', True)
                                      
                    case SpecialProcessingType.PAYDAY:
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
                    
                    case SpecialProcessingType.HOLIDAY:    # a.k.a. Spring Break, Holiday
                        # the number of hearts you get is configured in the specialProcessing section
                        # pending_action  "stay_or_move" - when a player's roll is in the must_roll list
                        # they must "resolve stay_or_move stay" in order to stay on the square and collect hearts[1]
                        # I know, complicated!
                        nhearts = self.special_processing.hearts[0] if player.on_holiday else self.special_processing.hearts[1]
                        player.add_hearts(nhearts)
                        player.on_holiday = True
                        player.add_pending_action(self.special_processing.pending_action, game_square_name=self.name, amount=0)
                        roll_str = f"rolled a {sum(dice)}. " if dice is not None else ""
                        message = f'Player {player.player_initials} {roll_str} {self.action_text}\n Collect {nhearts} {GameConstants.HEART}s'
                        result = CommandResult(CommandResult.SUCCESS, message, True)
                    
                    case SpecialProcessingType.BUY_INSURANCE:
                        player.pending_action = self.special_processing.pending_action
                        # resolve with "resolve buy_insurance n"   where n is the number of policies to buy
                        result = CommandResult(CommandResult.NEED_PLAYER_CHOICE, f'Player {player.player_initials} may buy insurance', False)
                    
                return result
            
            case BorderSquareType.DANGER_SQUARE:   # IncomeTax, DonateNow, CarPayment, PayRent, ShoppingSpree, DivorceCourt
                sp_type = self.special_processing.processing_type    # special processing type independent of the square name
                payment = self.special_processing.compute_cash_loss(player)
                player.add_cash(-payment)       # this will set the bankrupt pending_action if cash is < 0 as a result
                player.add_point_loss("cash", payment)    # covered by insurance
                if player.is_computer_player() and player.is_insured and (payment >= player.insurance_premium):
                    # use insurance
                    next_action = 'use_insurance'    # this will add back the amount paid
                    result =  CommandResult(CommandResult.SUCCESS, \
                                f"Player {player.player_initials} uses insurance to cover {payment} payment", True, next_action=next_action)
                else:
                    result =  CommandResult(CommandResult.SUCCESS, f'{self.action_text}\n Player {player.player_initials}  pays {payment}, remaining cash: {player.cash}', player.cash < 0)
            case _:
                result = CommandResult(CommandResult.SUCCESS, f'{self.square_type} {self.name} execute not yet implemented', False)   #  TODO
                
        return result
    
    def execute_special_processing(self, player:Player, dice:List[int]=None, **kwargs):
        """Invokes the specialProcessing section of this border square for a player.
            Arguments:
                player - the current Player (who landed on this border square)
                dice - optional, the player's dice roll
            Returns: CommandResult
            
            This method is called as exit processing for a square or as needed, whereas execute() is called when a player lands on a border square.
            
            TODO - finish this, for now return SUCCESS
        """
        sp_type = self.special_processing.processing_type
        result = None
        match(sp_type):
            case SpecialProcessingType.UNEMPLOYMENT | SpecialProcessingType.HOSPITAL:
                #
                # check the roll against "must_roll" and "require_doubles"
                #
                num_spaces = sum(dice)
                can_roll =  num_spaces in self.special_processing.must_roll or (self.special_processing.require_doubles and dice[0] == dice[1])
                if can_roll:
                    result = CommandResult(CommandResult.SUCCESS, f'Player can leave {self.name}', True)
                    if sp_type is SpecialProcessingType.UNEMPLOYMENT:
                        player.is_unemployed = False
                    else:
                        player.is_sick = False
                else:
                    result = CommandResult(CommandResult.EXECUTE_NEXT, f'Player rolled {dice} and must remain in {self.name}', True, next_action="next")
                
            case SpecialProcessingType.GAMBLE:
                result = self.special_processing.gamble(player)
            
            case SpecialProcessingType.BUY_HEARTS | SpecialProcessingType.BUY_STARS:
                result = self.special_processing.buy_points(player, **kwargs)
            
            case SpecialProcessingType.BUY_EXPERIENCE:    # should never get here
                result = CommandResult(CommandResult.ERROR, f'Internal game engine error execute_special_processing({kwargs["what"]})')
                
            case _:
                result = CommandResult(CommandResult.SUCCESS, f'{self.square_type} {self.name} execute_special_processing not yet implemented', False)
        
        return result
    
    def update_board_location(self, player:Player):
        player.board_location.border_square_number = self.number
        player.board_location.border_square_name = self.name
        player.board_location.occupation_name = None     
        
    def to_JSON(self):
        return json.dumps(self.game_square_dict)

    