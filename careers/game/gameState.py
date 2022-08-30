'''
Created on Aug 15, 2022

@author: don_bacon
'''
from datetime import datetime
from game.player import Player
from game.careersObject import CareersObject

class GameState(CareersObject):
    """Maintains the global state of a Careers game instance.
    
    """


    def __init__(self, total_points):
        """Create and initialize a Careers GameState
            The GameState encapsulates the following dynamic game state properties:
                number_of_players
                players - a [Player]
                current_player_number -  the current player number (whose turn it is)
                current_player - a Player instance
                winning_player - a Player instance, None until the game determines a winner
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
        self._seconds_remaining = 0
        self._game_type = 'points'
    
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
    
    @property
    def turn_number(self):
        return self._turn_number
    
    @property
    def seconds_remaining(self):
        return self._seconds_remaining

    def next_player_number(self):
        """Returns the player number of the next player. And sets the value of current_player.
        
        """
        p = self.current_player_number + 1
        if p >= self.number_of_players:
            self.current_player_number = 0
        else:
            self.current_player_number = p
        self.current_player = self.players[self.current_player_number]
        return self.current_player_number
    
    def add_player(self, aplayer:Player):
        """Add a Player to the game and increments the number_of_players.
        
        """
        aplayer.number = self.number_of_players     # starts at 0
        self._players.append(aplayer)
        self._number_of_players += 1
    
    def to_JSON(self):
        
        jstr = "{\n"
        jstr += f' "game_type" : "{self.game_type}",\n'
        jstr += f' "number_of_players" : "{self.number_of_players}",\n'
        jstr += f' "current_player_number" : "{self.current_player_number}",\n'
        jstr += f' "turns" : "{self.turns}",\n'
        jstr += f' "turn_number" : "{self.turn_number}",\n'
        jstr += f' "total_points" : "{self.total_points}",\n'
        jstr += f' "seconds_remaining" : "{self.seconds_remaining}",\n'
        if self.winning_player is not None:
            jstr += f' "winning_player" : "{self.winning_player.initials}",\n'
        jstr += ' "players" : [\n'
        i = 1
        for player in self.players:
            jstr += player.to_JSON()
            if i < self.number_of_players:
                jstr += ",\n"
            else:
                jstr += "\n"
            i += 1
        jstr += "],\n"
        jstr += f' "game_complete" : "{self.game_complete}"\n'
        jstr += "}\n"
        return jstr
        