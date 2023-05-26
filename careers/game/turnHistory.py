'''
Created on May 21, 2023

@author: don_bacon
'''

from game.careersObject import CareersObject
from game.successFormula import SuccessFormula
from dataclasses import dataclass, field
from typing import List, Dict
import json, logging

@dataclass
class Turn():
    """
        A data class encapsulating the components of a player's turn
        
    """
    player_number:int
    turn_number:int
    commands:List[str]=field(default_factory=list)     # list of the commands executed this turn
    outcome:int=0           # calculated outcome

    points:int=0            # number of points gained or lost
    opportunities:int=0     # number of Opportunity cards gained or lost
    experiences:int=0       # number of Experience cards gained or lost
    sick:int=0              # -1 if a player is in the Hospital at the end of the Turn, 0 otherwise
    unemployed:int=0      # -1 if a player is in the Unemployment at the end of the Turn, 0 otherwise
    degrees:int=0           # number of degrees earned this Turn
    occupations:int=0       # number of occupations/careers completed
    salary:int=0            # Sum of salary increases and decreases as points (so $3000 salary bump = 3)
    opportunity_card_value:int=0  # sum of the card values of the Opportunity cards gained. Negative value if a card is lost or used.
    experience_card_value:int=0   # sum of the card values of the Experience cards gained. Negative value if a card is lost or used.
    cash:int=0              # net gain/loss in cash on hand
    stars:int=0             # net gain/loss in Fame points (stars)
    hearts:int=0            # net gain/loss in Happiness points (hearts)
    can_retire:int=0        # 1=yes, 0 = not yet or already retired
    # Goal fulfillment has a value of 0 or 1 for each goal component (cash, stars, hearts).  
    # 0 if no net change. 1 if the goal is fulfilled.
    cash_goal:int=0
    hearts_goal:int=0
    stars_goal:int=0
        
    def to_dict(self) -> dict:
        turn_dict = {"turn" : {  "player_number" : self.player_number, "turn_number" : self.turn_number, \
                    "commands" : self.commands, \
                    "outcome": self.outcome, "points" : self.points, \
                    "opportunities" : self.opportunities, "experiences" : self.experiences, \
                    "sick" : self.sick, "unemployed" : self.unemployed, "degrees" : self.degrees, \
                    "occupations" : self.occupations, "salary" : self.salary, \
                    "opportunity_card_value" : self.opportunity_card_value, \
                    "experience_card_value" : self.experience_card_value, \
                    "cash" : self.cash, "stars" : self.stars, "hearts" : self.hearts, "can_retire" : self.can_retire, \
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
            return (self.points, self.opportunities, self.experiences, self.sick, self.unemployed, \
                    self.degrees, self.occupations, self.salary, \
                    self.opportunity_card_value, self.experience_card_value, self.cash, self.stars, self.hearts, self.can_retire) == \
                    (other.points, other.opportunities, other.experiences, other.sick, other.unemployed, \
                     other.degrees, other.occupations, other.salary, \
                    other.opportunity_card_value, other.experience_card_value, other.cash, other.stars, other.hearts, other.can_retire)
        
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
        outcome = self._turn_outcome(turn, before_info, after_info)
        turn.outcome = outcome
        self.add_turn(turn)
        return turn
    
    def get_player_info(self, turn_number:int) -> Dict:
        return self._player_info[turn_number] if turn_number < len(self._player_info) else {}
    
    def add_turn(self, turn:Turn) ->int:
        self._turns.append(turn)
        return len(self._turns)
    
    def get_turn(self, index:int=-1) ->Turn :
        return self._turns[index]

    def _turn_outcome(self, turn, before_info, after_info) -> int:
        """
            Compute and save the outcome of a turn
        """
        outcome = 0
        info_diff = self.diff_info(before_info, after_info)
        for key in info_diff.keys():
            diff = info_diff[key]
            outcome += self._turn_outcome_parameters[key] * diff
            exec_string = f"turn.{key} = {diff}"
            logging.debug(f"exec: {exec_string}")
            exec(exec_string)
        
        return outcome
    
    def diff_info(self, before_info:Dict, after_info:Dict) ->Dict:
        '''Essentially after_info - before_info for each info dictionary key. Sample info:
            {"player": "DWB", "salary": 6000, 
             "progress": {"cash": 9000, "stars": 14, "hearts": 2, "points": 25}, 
             "insured": false, "unemployed": false, "sick": false, "extra_turn": 0, "can_retire": false, "net_worth": 9000, "pending_actions": [], 
             "success_formula": {"cash": 40, "stars": 10, "hearts": 50, "points": 100}, 
             "degrees": {"number_of_degrees": 2, "degrees": {"Law": 1, "Marketing": 1}}}

        '''
        info_diff = {}
        if after_info["salary"] != before_info["salary"]:
            diff =  int((after_info["salary"] - before_info["salary"])/1000)
            info_diff.update({"salary" : diff})
            
        points_before = before_info["progress"]["points"]
        points_after = after_info["progress"]["points"]
        if points_after != points_before:
            diff = points_after - points_before
            info_diff.update({"points" : diff})
        
        unemployed_before = before_info["unemployed"]
        unemployed_after = after_info["unemployed"]
        if unemployed_after != unemployed_before:
            diff = unemployed_after - unemployed_before
            info_diff.update({"unemployed":diff})
        
        sick_before = before_info["sick"]
        sick_after = after_info["sick"]
        if sick_before != sick_after:
            diff =  sick_after - sick_before
            info_diff.update({"sick":diff})
            
        unemployed_before = before_info["unemployed"]
        unemployed_after = after_info["unemployed"]
        if unemployed_before != unemployed_after:
            diff =  unemployed_after - unemployed_before
            info_diff.update({"unemployed":diff}) 
            
        # check success formula goals (cash, stars, hearts) that have been completed this turn
        cash_before = before_info["progress"]["cash"]
        stars_before = before_info["progress"]["stars"]
        hearts_before = before_info["progress"]["hearts"]
        cash_after = after_info["progress"]["cash"]
        stars_after = after_info["progress"]["stars"]
        hearts_after = after_info["progress"]["hearts"]
        if cash_before != cash_after:
            diff = int((cash_after -  cash_before)/1000)
            info_diff.update({"cash":diff})
            cash_goal = cash_after >= self.success_formula.money
            info_diff.update({"cash_goal":cash_goal})
            
        if stars_before != stars_after:
            diff = stars_after - stars_before
            info_diff.update({"stars":diff})
            stars_goal = stars_after >= self.success_formula.stars
            info_diff.update({"stars_goal":stars_goal})
            
        if hearts_before != hearts_after:
            diff =  hearts_after - hearts_before
            info_diff.update({"hearts":diff})
            hearts_goal = hearts_after >= self.success_formula.hearts
            info_diff.update({"hearts_goal":hearts_goal})

        retire_before = before_info["can_retire"]
        retire_after = after_info["can_retire"]
        if retire_after != retire_before:
            diff = retire_after - retire_before
            info_diff.update({"can_retire":diff})
            
        opportunities_before = before_info["opportunities"]
        experiences_before = before_info["experiences"]
        opportunities_after = after_info["opportunities"]
        experiences_after = after_info["experiences"]       
        if opportunities_after != opportunities_before:
            diff = opportunities_after - opportunities_before
            info_diff.update( {"opportunities": diff})
        if experiences_after != experiences_before:
            diff = experiences_after - experiences_before
            info_diff.update( {"experiences": diff})
            
        return info_diff
            
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
    