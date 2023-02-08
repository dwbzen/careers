'''
Created on Aug 12, 2022

@author: don_bacon
'''

from game.player import  Player
from game.careersGameEngine import CareersGameEngine
from game.commandResult import CommandResult
from game.gameConstants import GameParametersType, GameType
from game.careersGame import CareersGame, restore_game
from game.gameState import GameState
import argparse, time

class GameRunner(object):
    """A command-line text version of Careers game play used for testing and simulating web server operation.
        Arguments:
            edition - the game edition: Hi-Tech or UK
            installationId - the installation ID to use
            game_type - points or timed
            total_points - total game points if a points game
            game_duration - total game duration if a timed game
            debug_flag - set to True for debugging output
            game_mode - 'test', 'prod', 'test-prod' or 'custom'
            gameid - the game ID of a previously saved game (in JSON format)
            restore - if True, restore a previously saved game 
            script - a script file to execute
            careers_game - a CareersGame instance. If not None, all previous parameters except debug_flag
              are set from careers_game
            
    """

    def __init__(self, edition:str, installationId:str, game_type:str, total_points:int, game_duration:int, debug_flag:bool,\
                  game_mode:str, careers_game:CareersGame|None=None, game_id:str|None=None):
        """
        Constructor
        """
        self._careersGame = careers_game
        self.game_engine = CareersGameEngine(careers_game=careers_game, game_id=game_id)
        self._debug = debug_flag          # traces the action by describing each step
        self.game_engine.debug = debug_flag
        
        if careers_game is None:    # new game
            self.total_points = total_points      # applies to GameType.POINTS
            self.game_duration = game_duration    # applies to GameType.TIMED
            self._edition = edition
            self._game_type = GameType[game_type.upper()]
        else:    # restored game
            self.total_points = careers_game.game_state.total_points             # applies to GameType.POINTS
            self.game_duration = careers_game.game_state.get_time_remaining()    # applies to GameType.TIMED
            self._edition = careers_game.edition_name
            self._game_type = careers_game.game_state.game_type
            # initialize CareersGameEngine with restored values
            self.game_engine.game_state = careers_game.game_state
            self.game_engine.careersGame = careers_game
            self.game_engine.gameId = game_id
        
        self._installationId = installationId
        self._game_mode = game_mode      # 'test', 'prod', 'test-prod' or 'custom'
        # these commands are not allowed in prod mode, but permitted in test, test_prod and custom modes
        self._restricted_commands = ["goto", "add_degree", "advance", "set"]
        self._action_commands = ["roll", "use", "bankrupt", "retire" ]    # increment turns for solo game

    def add_player(self, name, initials, player_id=None, email=None, stars=0, hearts=0, cash=0):
        self.game_engine.add(name, initials, player_id, email, stars, hearts, cash)
    
    @property
    def trace(self):
        return self._trace
    
    @trace.setter
    def trace(self, value):
        self._trace = value
        
    @property
    def careersGame(self) -> CareersGame:
        return self._careersGame
    
    @careersGame.setter
    def careersGame(self, value):
        self._careersGame = value
    
    @property
    def master_id(self):
        return self._master_id
    
    @property
    def game_mode(self)->str:
        return self._game_mode
    
    @property
    def game_type(self)->GameType:
        return self._game_type
    
    def number_of_players(self):
        return self.game.game_state.number_of_players
    
    def get_game_state(self) -> GameState:
        return self.careersGame.game_state
    
    def create_game(self, game_id=None, game_parameters_type="prod") -> CommandResult:
        total_points = self.total_points if self.game_type is GameType.POINTS else self.game_duration
        result = self.game_engine.create(self._edition, self._installationId, self.game_type.value, total_points, game_id, game_parameters_type)
        self._careersGame = self.game_engine.careersGame
        return result
    
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
        
        while not game_over:
            for i in range(nplayers):
                # 
                current_player = game_state.current_player
                pn = current_player.number
                done = False
                while not done:
                    turn_number = game_state.turn_number
                    prompt = f'player {pn} {current_player.player_initials} ({turn_number}): '
                    cmd = input(prompt)
                    if len(cmd) == 0: continue
                    cmd_str = cmd.split(" ")
                    
                    if cmd_str[0] in self._restricted_commands \
                      and self.game_mode != "test_prod" \
                      and self._careersGame.game_parameters_type is GameParametersType.PROD:
                        print( f"'{cmd_str[0]}' command not allowed in production mode")
                        continue
                    result = self.execute_command(cmd, current_player)
                    print(result.message)
                    done = result.done_flag
                    if result.return_code == CommandResult.TERMINATE:
                        game_over = True
                    if nplayers == 1 and cmd_str[0] in self._action_commands:
                        game_state.increment_turns()
                if game_over:
                    break
        
        self.game_engine.end()
        
    def run_script(self, filePath:str, delay:int, log_comments=True):

        turn_number = 1
        game_state = self.get_game_state()
        current_player = None
        fp = open(filePath, "r")
        scriptText = fp.readlines()
        fp.close()
        for line in scriptText:
            if len(line) > 0:
                cmd = line[:-1]   # drop the trailing \n
                if len(cmd) == 0:
                    continue
                elif cmd.startswith("#"):    # comment line
                    if log_comments:
                        result = self.execute_command(f'log_message {cmd}', current_player)
                    else:
                        result = None
                elif cmd.startswith("add player "):
                    result = self.execute_command(cmd, None)
                else:
                    current_player = game_state.current_player
                    result = self.execute_command(cmd, current_player)
                    turn_number += 1
                
                if result is not None:    
                    print(f'"{cmd}": {result.message}')
                    if result.return_code == CommandResult.TERMINATE:
                        break
                time.sleep(delay)
                
        self.game_engine.end()


def main():
    parser = argparse.ArgumentParser(description="Run a command-driven Careers Game for 1 to 6 players")
    parser.add_argument("--players", "-p", help="The number of players", type=int, choices=range(1,6), default=1)
    parser.add_argument("--points", help="Total game points", type=int, choices=range(30, 10000), default=100)
    parser.add_argument("--time", help="For a timed game, the game duration in minutes", type=int, choices=range(5, 24*60), default=30)
    parser.add_argument("--params", help="Game parameters type: 'test', 'prod', 'test-prod' or 'custom' ", type=str, \
                        choices=["test","prod","custom","test_prod"], default="test")
    parser.add_argument("--gameid", help="Game ID", type=str, default=None)
    parser.add_argument("--edition", help="Game edition: Hi-Tech or UK", type=str, choices=["Hi-Tech", "UK"], default="Hi-Tech")
    parser.add_argument("--script", help="Execute script file", type=str, default=None)
    parser.add_argument("--delay", help="Delay a specified number of seconds between script commands", type=int, default=0)
    parser.add_argument("--comments", "-c", help="Log comment lines when running a script", type=str, choices=['y','Y', 'n', 'N'], default='Y')
    parser.add_argument("--debug", "-d", help="Run in debug mode, logging trace output",  action="store_true", default=False)
    parser.add_argument("--type","-t", help="Game type: points, timed", type=str, choices=["points", "timed"], default="points")
    parser.add_argument("--restore", "-r", help="Restore game by gameid", action="store_true", default=False)
    args = parser.parse_args()
    
    total_points = args.points
    game_duration = args.time
    edition = args.edition
    game_type = args.type            # 'points' or 'timed'
    installationId = 'ZenAlien2013'  # uniquely identifies 'me' as the game creator
    filePath = args.script           # complete file path
    log_comments = args.comments.lower()=='y'
    careers_game = None
    
    gameId = args.gameid
    current_player = None
    if args.restore:
        careers_game = restore_game(gameId)
        nplayers = careers_game.game_state.number_of_players
        game_runner = GameRunner(edition, installationId, game_type, total_points, game_duration, args.debug, args.params, careers_game=careers_game, game_id=gameId)
        current_player = game_runner.get_game_state().current_player
    else:
        #
        # test_prod allows goto and advance in production mode
        #
        game_parameters_type = "prod" if args.params=="test_prod" else args.params    # not used if restoring a previously saved CareersGame
        game_runner = GameRunner(edition, installationId, game_type, total_points, game_duration, args.debug, args.params)
    
        # creates a CareersGame for points
        game_runner.create_game(gameId, game_parameters_type)
        
        if filePath is not None:
            game_runner.run_script(filePath, args.delay, log_comments=log_comments)
        else:
            #
            # add players
            #
            nplayers = args.players
            
            # name, initials=None, player_id=None, email=None, stars=0, hearts=0, cash=0
            # use update command to add success_formula if not provided here
            game_runner.execute_command("add player Don DWB dwb20221206 dwbzen@gmail.com 40 10 50", None)
            if nplayers >= 2:
                game_runner.execute_command("add player Brian BDB bdb20221206 brian.bacon01@gmail.com 50 20 30", None)
            if nplayers >= 3:
                game_runner.execute_command("add player Cheryl CJL cjl20221206 Lister.Cheryl@gmail.com 10 50 40", None)
            if nplayers == 4:
                game_runner.execute_command("add player Scott SFP scott20230125 scotty121382@yahoo.com 30 30 40", None)
    
    game_runner.execute_command("start", current_player)
    game_runner.run_game()
    
if __name__ == '__main__':
    main()
    
