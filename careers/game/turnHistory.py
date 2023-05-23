'''
Created on May 21, 2023

@author: don_bacon
'''

from game.careersObject import CareersObject
from game.successFormula import SuccessFormula
from dataclasses import dataclass, field
from typing import List, Dict
import json

@dataclass
class Turn():
    """
        A data class encapsulating the components of a player's turn
        
    """
    player_number:int
    turn_number:int
    commands:List[str]=field(default_factory=list)
    outcome:int=0           # calculated outcome

    points:int=0            # number of points gained or lost
    opportunities:int=0     # number of Opportunity cards gained or lost
    experiences:int=0       # number of Experience cards gained or lost
    hospital:int=0          # -1 if a player is in the Hospital at the end of the Turn, 0 otherwise
    unemployment:int=0      # -1 if a player is in the Unemployment at the end of the Turn, 0 otherwise
    degrees:int=0           # number of degrees earned this Turn
    occupations:int=0       # number of occupations/careers completed
    salary:int=0            # Sum of salary increases and decreases as points (so $3000 salary bump = 3)
    opportunity_card_value:int=0  # sum of the card values of the Opportunity cards gained. Negative value if a card is lost or used.
    experience_card_value:int=0   # sum of the card values of the Experience cards gained. Negative value if a card is lost or used.
    cash:int=0              # net gain/loss in cash on hand
    stars:int=0             # net gain/loss in Fame points (stars)
    hearts:int=0            # net gain/loss in Happiness points (hearts)
    # Goal fulfillment has a value of -1, 0 or 1 for each goal component (cash, stars, hearts).  
    # A value of -1 if a previously fulfilled goal becomes short because of some loss (like half your cash).  
    # 0 if no net change. 1 if the goal is fulfilled.
    cash_goal:int=0
    hearts_goal:int=0
    stars_goal:int=0
        
    def to_dict(self) -> dict:
        turn_dict = {"turn" : {  "player_number" : self.player_number, "turn_number" : self.turn_number, \
                    "commands" : self.commands, \
                    "outcome": self.outcome, "points" : self.points, \
                    "opportunities" : self.opportunities, "experiences" : self.experiences, \
                    "hospital" : self.hospital, "unemployment" : self.unemployment, "degrees" : self.degrees, \
                    "occupations" : self.occupations, "salary" : self.salary, \
                    "opportunity_card_value" : self.opportunity_card_value, \
                    "experience_card_value" : self.experience_card_value, \
                    "cash" : self.cash, "stars" : self.stars, "hearts" : self.hearts, \
                    "cash_goal" : self.cash_goal, "stars_goal" : self.stars_goal, "hearts_goal" : self.hearts_goal } }
        return turn_dict
    
    def __repr__(self):
        """Returns the Turn in JSON format
        """
        return json.dumps(self.to_dict(), indent=2)
    
    def to_JSON(self):
        return self.__repr__()
    
    def __eq__(self, other):
        if isinstance(other, Turn):
            return (self.points, self.opportunities, self.experiences, self.hospital, self.unemployment, \
                    self.degrees, self.occupations, self.salary, \
                    self.opportunity_card_value, self.experience_card_value, self.cash, self.stars, self.hearts) == \
                    (other.points, other.opportunities, other.experiences, other.hospital, other.unemployment, \
                     other.degrees, other.occupations, other.salary, \
                    other.opportunity_card_value, other.experience_card_value, other.cash, other.stars, other.hearts)
        
        return NotImplemented


class TurnHistory(CareersObject):
    """ History of a player's turn, including command(s), and outcomes.
    """
    
    BEFORE_KEY = "info_before"
    AFTER_KEY = "info_after"

    def __init__(self, player_number:int, turn_outcome_parameters:dict, success_formula:SuccessFormula=None):
        """
        
        """
        self._player_number = player_number
        self._turn_number = 0       # first turn has turn_number == 0
        self._turn_outcome_parameters = turn_outcome_parameters
        self._turns:List[Turn] = list()
        # player_info is a List[dict] with keys "info_before" and "info_after"
        # info_before is the player's info at the start of the turn
        # info_after is the player's info after the turn is completed
        # The deltas between the two are used to compute the outcome
        # The index of the list is the corresponding turn number.
        self._player_info:List[Dict] = list()
        self._success_formula = success_formula
        
    @property
    def player_number(self) -> int:
        return self._player_number
    
    @property
    def turn_outcome_parameters(self) -> Dict:
        return self._turn_outcome_parameters
    
    @property
    def turn_number(self) ->int:
        return self._turn_number
    
    @turn_number.setter
    def turn_number(self, value):
        self._turn_number = value
    
    def next_turn_number(self):
        return self._turn_number + 1
    
    @property
    def turns(self) ->List[Turn] :
        return self._turns
    
    @property
    def player_info(self) ->List[Dict]:
        return self._player_info
    
    @property
    def success_formula(self) ->SuccessFormula:
        return self._success_formula
    
    @success_formula.setter
    def success_formula(self, value:SuccessFormula):
        self._success_formula = value
    
    def add_player_info(self, turn_number:int, key:str, player_info:Dict):
        assert key is not None 
        if key==TurnHistory.BEFORE_KEY or key==TurnHistory.AFTER_KEY:
            i = len(self._player_info) - 1
            if i==turn_number:
                self._player_info[i].update( {key:player_info })
            else:
                self._player_info.append({key:player_info })
        else:
            return NotImplemented
        
    def create_turn(self, turn_number) ->Turn:
        """Create and add a new Turn object from the player_info BEFORE and AFTER deltas
            After creating the Turn, calculate the outcome.
        """
        before_info = self._player_info[turn_number][TurnHistory.BEFORE_KEY]
        after_info = self._player_info[turn_number][TurnHistory.AFTER_KEY]
        turn = Turn(self._player_number, turn_number)
        
        self.add_turn(turn)
        return turn
    
    def get_player_info(self, turn_number:int) -> Dict:
        return self._player_info[turn_number] if turn_number < len(self._player_info) else {}
    
    def add_turn(self, turn:Turn) ->int:
        self._turns.append(turn)
        return len(self._turns)
    
    def get_turn(self, index:int=-1) ->Turn :
        return self._turns[index]

    def turn_outcome(self) -> int:
        """
            Compute and save the value of a turn
        """
        return 0
    
    def size(self) ->int:
        return len(self._turns)
    
    def to_dict(self) ->Dict:
        hist = {"turns" : list(), "player_info" : list()}
        if self.size()==0:
            return hist
        for turn in self._turns:
            hist["turns"].append(turn.to_dict())
        for player_info in self._player_info:
            hist["player_info"].append(player_info)
        return hist

    def to_JSON(self):
        """Returns a JSON formatted string of all the Turns in the history.
        """
        return json.dumps(self.to_dict(), indent=1)
    