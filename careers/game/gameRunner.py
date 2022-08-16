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
        self._trace = True          # traces the action by describing each step
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
    
    def get_game_state(self):
        return self.game_engine.game_state
    
    def execute_command(self, cmd, aplayer):
        """Command format is command name + optional arguments
            The command and arguments passed to the game engine for execution
        
        """
        command = cmd.split(" ")     # TODO
        if len(command) > 1:
            args = command[1:]
        else:
            args = []
        result = self.game_engine.execute_command(command[0], args, aplayer)
    
    def run_game(self):
        self.game_engine = CareersGameEngine(self.game)
        self.game_engine.trace = self.trace
        self.game_engine.start()
        game_over = False
        game_state = self.get_game_state()
        nplayers = game_state.number_of_players
        turn_number = 1
        while not game_over:
            for i in range(nplayers):
                pn = game_state.next_player_number()
                current_player = game_state.current_player
                prompt = f'{current_player.player_initials} ({turn_number}): '
                cmd = input(prompt)
                if cmd=='quit':
                    game_over = True
                    break
                else:
                    self.execute_command(cmd, current_player)
            turn_number += 1
        
        self.game_engine.end()
        

if __name__ == '__main__':

    total_points = 100
    game_runner = GameRunner(total_points)
    
    game_runner.add_player('Don', 'DWB', stars=40, hearts=10, cash=50)
    game_runner.add_player('Scott','SFP', stars=20, hearts=40, cash=40)
    
    game_runner.run_game()
    
    