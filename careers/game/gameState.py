'''
Created on Aug 15, 2022

@author: don_bacon
'''
from datetime import datetime
import json
from game.player import Player
from game.careersObject import CareersObject

class GameState(CareersObject):
    """Maintains the global state of a Careers game instance.
    
    """


    def __init__(self, game_id, total_points, game_type='points'):
        """Create and initialize a Careers GameState
            The GameState encapsulates the following dynamic game state properties:
                number_of_players
                players - a [Player]
                current_player_number -  the current player number (whose turn it is)
                current_player - a Player instance
                winning_player - a Player instance, None until the game determines a winner
                total_points - points needed to win if game_type is 'points', else it's the #minutes in a timed game
                turns - total number of completed turns taken by all players
                turn_number - the current turn number
                game_start - the datetime when the game started (when this object was created)
                seconds_remaining - number of seconds remaining if a timed game
                game_type - 'points' (the default) or 'timed'
        """
        self._number_of_players = 0
        self._players = []   # list of Player
        self._current_player_number = -1
        self._current_player = None
        self._total_points = total_points
        self._winning_player = None
        self._turns = 0
        self._turn_number = 1
        self._game_start = datetime.now()
        self._game_complete = False
        
        self._game_type = game_type
        self._seconds_remaining = 0 if game_type=='points' else total_points * 60
        self._gameId = game_id
    
    @property
    def gameId(self):
        return self._gameId
    
    @gameId.setter
    def gameId(self, value):
        self._gameId = value
    
    @property
    def number_of_players(self):
        return self._number_of_players
    
    @number_of_players.setter
    def number_of_players(self, value):
        self._number_of_players = value

    @property
    def players(self):
        return self._players
    
    @property
    def winning_player(self):
        return self._winning_player
    
    @property
    def current_player(self):
        return self._current_player
    
    @current_player.setter
    def current_player(self, value):
        self._current_player = value
    
    @property
    def current_player_number(self):
        return self._current_player_number
    
    @current_player_number.setter
    def current_player_number(self, value):
        self._current_player_number = value
        
    @property
    def game_type(self):
        return self._game_type
    
    @property
    def game_complete(self):
        return self._game_complete
    
    @property
    def total_points(self):
        return self._total_points
    
    @property
    def turns(self):
        return self._turns
    
    @turns.setter
    def turns(self, value):
        self._turns = value
    
    @property
    def turn_number(self):
        return self._turn_number
    
    @turn_number.setter
    def turn_number(self, value):
        self._turn_number = value
    
    @property
    def seconds_remaining(self):
        return self._seconds_remaining

    def set_next_player(self):
        """Returns the player number of the next player. And sets the value of current_player.
            If the next player has lose_turn == True, the current_player is set to the next player
            after that player and their lose_turn flag is reset to False.
        
        """
        npn = self._get_next_player_number()
        if self.players[npn].lose_turn:
            self.current_player_number = npn
            self.players[npn].lose_turn = False
            npn = self._get_next_player_number()
            
        self.current_player_number = npn
        self.current_player = self.players[self.current_player_number]
        self.current_player.can_roll = True
        if npn == 0:
            self.turns += 1
            self.turn_number += 1
            
        return self.current_player_number
    
    def _get_next_player_number(self):
        p = self.current_player_number + 1
        if p >= self.number_of_players:
            return 0
        else:
            return p
    
    def add_player(self, aplayer:Player):
        """Add a Player to the game and increments the number_of_players.
        
        """
        aplayer.number = self.number_of_players     # starts at 0
        self._players.append(aplayer)
        self._number_of_players += 1
    
    def get_player_by_initials(self, initials):
        player = None
        for p in self.players:
            if p.player_initials.lower() == initials.lower():
                player = p
                break
        return player
    
    def to_JSON(self):
        
        gs = {"gameId" : self._gameId, "game_type" : self.game_type, "number_of_players" : self.number_of_players, "current_player_number" : self.current_player_number }
        gs["turns"] = self.turns
        gs["turn_number"] = self.turn_number
        gs["total_points"] = self.total_points
        gs["seconds_remaining"] = self.seconds_remaining
        if self.winning_player is not None:
            gs["winning_player"] = self.winning_player.initials
        gs["game_complete"] = self.game_complete
        #gs["players"] 

        players = []
        for player in self.players:
            players.append(player.to_dict())
        gs["players"] = players

        return json.dumps(gs, indent=2)
        