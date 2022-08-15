'''
Created on Aug 12, 2022

@author: don_bacon
'''

from game.careersGame import CareersGame
from game.successFormula import SuccessFormula
from game.player import  Player
from game.careersGameEngine import CareersGameEngine

class GameRunner(object):
    """A command-line text version of Careers game play used for testing.
        Uses a default game of 100 points and 2 players.
    """

    def __init__(self, total_points):
        """
        Constructor
        """
        self.game = CareersGame('Hi-Tech', total_points)
        self.total_points = total_points
        self._trace = True         # traces the action by describing each step
        self.game_engine = None     # CareersGameEngine
        

    def add_player(self, name, initials, stars=0, hearts=0, cash=0):
        sf = SuccessFormula(stars=stars, hearts=hearts, cash=cash)
        player = Player(name=name, initials=initials)
        player.success_formula = sf
        player.salary = self.game.game_parameters['starting_salary']
        player.cash = self.game.game_parameters['starting_cash']
        self.game.add_player(player)        # adds to GameState
    
    @property
    def trace(self):
        return self._trace
    
    @trace.setter
    def trace(self, value):
        self._trace = value
    
    def number_of_players(self):
        return self.game.game_state.number_of_players
    
    def run_game(self):
        if(self.trace):
            print(f'Starting game with {self.number_of_players()} players ')
        self.game_engine = CareersGameEngine(self.game)
        
        if(self.trace):
            print("Game over")
        

if __name__ == '__main__':

    total_points = 100
    game_runner = GameRunner(total_points)
    
    game_runner.add_player('Don', 'DWB', stars=40, hearts=10, cash=50)
    game_runner.add_player('Scott','SFP', stars=20, hearts=40, cash=40)
    
    game_runner.run_game()
    
    
