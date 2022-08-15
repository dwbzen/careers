'''
Created on Aug 15, 2022

@author: don_bacon
'''
from datetime import datetime
from game.player import Player

class GameState(object):
    """Maintains the global state of a Careers game instance.
    
    """


    def __init__(self, total_points):
        '''
        Constructor
        '''
        self._number_of_players = 0
        self._players = []   # list of Player
        self._current_player_number = 0     # the current player number
        self._current_player = None         # Player reference
        self._total_points = total_points
        self._winning_player = None         # Player reference
        self._turns = 0                     # total number of turns completed
        self._turn_number = 1               # current turn#
        self._game_start = datetime.now()
        self._game_complete = None
    
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
        
        