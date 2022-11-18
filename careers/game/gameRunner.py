'''
Created on Aug 12, 2022

@author: don_bacon
'''

from game.player import  Player
from game.careersGameEngine import CareersGameEngine
from game.commandResult import CommandResult
import argparse

class GameRunner(object):
    """A command-line text version of Careers game play used for testing and simulating web server operation.
    """

    def __init__(self, edition, master_id, game_type, total_points):
        """
        Constructor
        """
        self._careersGame = None
        self.total_points = total_points
        self._trace = True          # traces the action by describing each step
        self._edition = edition
        self._game_type = game_type
        self.game_engine = CareersGameEngine()
        self.game_engine.trace = self._trace
        self._master_id = master_id

    def add_player(self, name, initials, stars=0, hearts=0, cash=0):
        self.game_engine.add(name, initials, stars, hearts, cash)
    
    @property
    def trace(self):
        return self._trace
    
    @trace.setter
    def trace(self, value):
        self._trace = value
        
    @property
    def careersGame(self):
        return self._careersGame
    
    @property
    def master_id(self):
        return self._master_id
    
    
    def number_of_players(self):
        return self.game.game_state.number_of_players
    
    def get_game_state(self):
        return self.game_engine.game_state
    
    def execute_command(self, cmd, aplayer:Player):
        """Command format is command name + optional arguments
            The command and arguments passed to the game engine for execution
            Arguments:
                cmd - the command string
                aplayer - a Player reference. If None, the engine executes the command as Administrator (admin) user.
            Returns:
                result - result dictionary (result, message, done)
        """

        args = []
            
        result = self.game_engine.execute_command(cmd, aplayer, args)
        return result
    
    def run_game(self):

        game_over = False
        game_state = self.get_game_state()
        nplayers = game_state.number_of_players
        turn_number = 1
        while not game_over:
            for i in range(nplayers):
                # 
                current_player = game_state.current_player
                pn = current_player.number
                done = False
                while not done:
                    prompt = f'player {pn} {current_player.player_initials} ({turn_number}): '
                    cmd = input(prompt)
                    result = self.execute_command(cmd, current_player)
                    print(result.message)
                    done = result.done_flag
                    if result.return_code == CommandResult.TERMINATE:
                        game_over = True
                if game_over:
                    break
            turn_number += 1
        
        self.game_engine.end()
        

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Run a command-driven Careers Game for 1 to 4 players")
    parser.add_argument("--players", "-p", help="the number of players", type=int, choices=range(1,5), default=1)
    parser.add_argument("--points", help="Total game points", type=int, choices=range(40, 10000), default=100)
    args = parser.parse_args()
    
    total_points = args.points
    edition = 'Hi-Tech'
    game_type = 'points'            # or 'timed'
    installationId = 'ZenAlien2013'      # uniquely identifies 'me' as the game creator
    game_runner = GameRunner(edition, installationId, game_type, total_points)  # creates a CareersGameEngine
    game_runner.execute_command(f'create {edition} {installationId} {game_type} {total_points}', None)     # creates a CareersGame for points
    #
    # add players
    #
    nplayers = args.players
    game_runner.execute_command("add player Don DWB 40 10 50", None)
    if nplayers >= 2:
        game_runner.execute_command("add player Brian BDB", None)    # use update command to add success_formula
    if nplayers >= 3:
        game_runner.execute_command("add player Beth Beth 30 30 40", None)
    if nplayers == 4:
        game_runner.execute_command("add player Cheryl CJL 10 50 40", None)
        
    game_runner.execute_command("start", None)
    
    game_runner.run_game()
    
    
