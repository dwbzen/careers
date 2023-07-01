'''
Created on Aug 12, 2022

@author: don_bacon
'''

from game.player import  Player
from game.careersGameEngine import CareersGameEngine
from game.commandResult import CommandResult
from game.gameConstants import GameParametersType, GameType, GameConstants
from game.careersGame import CareersGame, restore_game
from game.gameState import GameState
import argparse, time
import logging

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
            game_id - the game ID of a previously saved game (in JSON format)
            restore - if True, restore a previously saved game 
            script - a script file to execute
            careers_game - a CareersGame instance. If not None, all previous parameters except debug_flag
              are set from careers_game
            
    """

    def __init__(self, edition:str, installationId:str, game_type:str, total_points:int, game_duration:int, loglevel:str,\
                  game_mode:str, careers_game:CareersGame|None=None, game_id:str|None=None):
        """
        Constructor
        """
        self._installationId = installationId
        self._game_mode = game_mode 
        self._edition = edition
        
        if careers_game is None:    # create a new game
            self._game_type = GameType[game_type.upper()]
            self.total_points = total_points      # applies to GameType.POINTS
            self.game_duration = game_duration    # applies to GameType.TIMED
            total_points = self.total_points if game_type is GameType.POINTS else self.game_duration
            
            self.game_engine = \
                CareersGameEngine(careers_game=None, game_id=None, loglevel=loglevel, edition=edition, installationId=installationId)

            result = self.game_engine.create(self._edition, self._installationId, self._game_type.value, total_points, game_mode)
            if result.return_code != CommandResult.SUCCESS:
                logging.error("Could not create a CareersGame")
            
            self._careersGame = self.game_engine.careersGame
            self._game_id = self._careersGame.gameId
            
        else:    # restore an existing game
            self._game_id = self._careersGame.gameId
            self.game_engine = CareersGameEngine(careers_game=careers_game, game_id=self.game_id, loglevel='warning', installationId=installationId)
            self.total_points = careers_game.game_state.total_points             # applies to GameType.POINTS
            self.game_duration = careers_game.game_state.get_time_remaining()    # applies to GameType.TIMED
            self._edition = careers_game.edition_name
            self._game_type = careers_game.game_state.game_type
            # initialize CareersGameEngine with restored values
            self.game_engine.game_state = careers_game.game_state
            self.game_engine.careersGame = careers_game
            self.game_engine.gameId = game_id
        
        debug_flag = loglevel == 'debug'
        self._debug = debug_flag          # traces the action by describing each step
        
        # 'test', 'prod', 'test-prod' or 'custom'
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
    
    @property
    def game_id(self) ->str:
        return self._game_id
    
    def number_of_players(self):
        return self.game.game_state.number_of_players
    
    def get_game_state(self) -> GameState:
        return self.careersGame.game_state
    
    def create_game(self, game_type:GameType, game_id=None, game_mode="prod") -> CommandResult:
        total_points = self.total_points if game_type is GameType.POINTS else self.game_duration
        
        result = self.game_engine.create(self._edition, self._installationId, game_type.value, total_points, game_id, game_mode)
        self._careersGame = self.game_engine.careersGame
        return result
    
    def execute_command(self, cmd, aplayer:Player) -> CommandResult:
        """Command format is command name + optional arguments
            The command and arguments passed to the game engine for execution
            Arguments:
                cmd - the command string
                aplayer - a Player reference. If None, the engine executes the command as Administrator (admin) user.
            Returns:
                result - result dictionary (result, message, done)
        """
            
        result = self.game_engine.execute_command(cmd, aplayer)
        return result
    
    def run_game(self):
        game_over = False
        game_state = self.careersGame.game_state
        nplayers = game_state.number_of_players
        
        while not game_over:
            for i in range(nplayers):
                # 
                current_player = game_state.current_player
                pn = current_player.number
                done = False
                while not done:
                    turn_number = game_state.turn_number
                    prompt = f'player {pn}, {current_player.player_initials}, turn={turn_number}: '
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
        """Runs a script file.
            A script file has one legit command or a statement per line.
            Use "add player..." to add players to the game, for example
            "add player Don DWB dwb20230113 dwbzen@gmail.com 20 10 30" for a 60 point game
            By default players are human. To add computer player, include "computer" as the last argument.
            For example "add player ComputerPlayer_1 CP_1 cp120230516 dwbzen@gmail.com 20 20 20 computer"
            Lines that begin with "# " are comments and are written to the log file as-is.
            Statements have Python syntax and are used to check results, control looping.
            All statements end in a "{" (for loop init), "}" (end loop) or ";" to differentiate from game commands.
            The following statements are supported:
            assignment
               (variable) = (value)
            looping
               while (expression) {
                   (statements and/or commands):
            logical
               if (variable) == (value):
                   (commands)
               else:
                   (commands)
            statements ending with ";"  are evaluated with the Python exec() or eval() functions.
            assignments are evaluated with exec(), "counter=1"  ->  exec("counter=1")
            The while condition is evaluated with eval(), "while counter<limit" -> eval("counter<limit")
            other statements evaluated with exec(), "counter+=1"  ->  exec("counter+=1")
            The logic assumes the loop body will be evaluated at least once.
        """
        turn_number = 1
        game_state = self.careersGame.game_state
        self.game_engine.automatic_run = True
        current_player = None
        fp = open(filePath, "r")
        scriptText = fp.readlines()
        fp.close()
        line_number = 0
        script_lines = len(scriptText)
        loop_start = -1
        loop_end = 0
        continue_loop = False
        #
        while line_number < script_lines:
            line = scriptText[line_number]
            if len(line) > 0:
                cmd = line.strip("\t\n ")   # drop tabs, spaces and  \n
                if len(cmd) == 0:
                    continue
                
                elif cmd.startswith("#"):    # comment line
                    if log_comments:
                        logging.debug(f'log_message {cmd}')
                        result = None
                    else:
                        result = None
                        
                elif cmd.startswith("add player "):
                    result = self.execute_command(cmd, None)
                    
                elif cmd.endswith(";"):    # use exec()
                    statement = cmd[:-1]
                    try:
                        exec(statement)
                        result = CommandResult(CommandResult.SUCCESS, statement, False)
                    except Exception as ex:
                        message = f'"{statement}" : Invalid exec statement\nexception: {str(ex)}'
                        result = CommandResult(CommandResult.ERROR,  message,  False, exception=ex)
                        logging.error(message)
                        
                elif cmd.endswith("{"):   # a while loop, execute the condition with eval()
                    condition = cmd[:-1][6:]    # assumes "while "
                    result = CommandResult(CommandResult.SUCCESS, condition, False)
                    try:
                        continue_loop = eval(condition)
                        if not continue_loop:
                            line_number = loop_end
                        else:
                            loop_start = line_number
                    except Exception as ex:
                        message = f'"{condition}" : Invalid eval statement\nexception: {str(ex)}'
                        result = CommandResult(CommandResult.ERROR,  message,  False, exception=ex)
                        logging.error(message)
                        
                elif cmd.endswith("}"):    # end of the loop
                    loop_end = line_number
                    line_number = loop_start - 1   # back to the while, -1 because line_number incremented below
                    result = CommandResult(CommandResult.SUCCESS, cmd, False)
                    
                else:
                    current_player = game_state.current_player
                    result = self.execute_command(cmd, current_player)
                    turn_number += 1
                
                if result is not None:
                    print(f'"{cmd}": {result.message}')
                    if result.return_code == CommandResult.TERMINATE:
                        break
                    
                line_number +=1
                time.sleep(delay)
                
        self.game_engine.end()


def main():
    parser = argparse.ArgumentParser(description="Run a command-driven Careers Game for 1 to 6 players, 0 to 2 computer players")
    parser.add_argument("--players", "-p", help="The number of human players", type=int, choices=range(1,6), default=1)
    parser.add_argument("--cp", help="The number of computer players", type=int, choices=range(0,3), default=0)
    parser.add_argument("--points", help="Total game points", type=int, choices=range(30, 10000), default=100)
    parser.add_argument("--time", help="For a timed game, the game duration in minutes", type=int, choices=range(5, 24*60), default=30)
    parser.add_argument("--params", help="Game parameters type: 'test', 'prod', 'test-prod' or 'custom' ", type=str, \
                        choices=["test","prod","custom","test_prod"], default="test")
    parser.add_argument("--gameid", help="Game ID", type=str, default=None)
    parser.add_argument("--edition", help="Game edition: Hi-Tech, Professions-Hi-Tech, JazzAge, or UK", \
                        type=str, choices=["Hi-Tech", "Professions-Hi-Tech", "UK", "JazzAge"], default="Hi-Tech")
    parser.add_argument("--script", help="Execute script file", type=str, default=None)
    parser.add_argument("--delay", help="Delay a specified number of seconds between script commands", type=int, default=0)
    parser.add_argument("--comments", "-c", help="Log comment lines when running a script", type=str, choices=['y','Y', 'n', 'N'], default='Y')
    # parser.add_argument("--debug", "-d", help="Run in debug mode, logging trace output",  action="store_true", default=False)
    parser.add_argument("--loglevel", help="Set Python logging level", type=str, choices=["debug","info","warning","error","critical"], default="warning")
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
        game_runner = GameRunner(edition, installationId, game_type, total_points, game_duration, \
                                 args.loglevel, args.params, careers_game=careers_game, game_id=gameId)
        current_player = game_runner.get_game_state().current_player
    else:
        #
        # test_prod allows goto and advance in production mode
        #
        game_mode = "prod" if args.params=="test_prod" else args.params    # not used if restoring a previously saved CareersGame
        game_runner = GameRunner(edition, installationId, game_type, total_points, game_duration, args.loglevel, game_mode)
        
        # creates a CareersGame for points
        # game_runner.create_game(gameId, game_parameters_type)
        
        if filePath is not None:
            game_runner.run_script(filePath, args.delay, log_comments=log_comments)
        else:
            #
            # add players
            #
            nplayers = args.players
            ncomputerPlayers = args.cp      # 0, 1 or 2 computer players
            
            # name, initials=None, player_id=None, email=None, cash=0, stars=0, hearts=0
            # use update command to add success_formula if not provided here
            game_runner.execute_command("add player Don DWB dwb20221206 dwbzen@gmail.com 40 10 50", None)
            if nplayers >= 2:
                game_runner.execute_command("add player Brian BDB bdb20221206 brian.bacon01@gmail.com 50 20 30", None)
            if nplayers >= 3:
                game_runner.execute_command("add player Cheryl CJL cjl20221206 Lister.Cheryl@gmail.com 10 50 40", None)
            if nplayers == 4:
                game_runner.execute_command("add player Scott SFP scott20230125 scotty121382@yahoo.com 30 30 40", None)
            
            if ncomputerPlayers > 0:
                for i in range(ncomputerPlayers):
                    name = f"CP_{i+1}"        # generate a computer name: CP_1, CP_2 etc.
                    add_cmd = f"add player {name} {name} {name}20230516 dwbzen@gmail.com 20 40 40 computer"
                    game_runner.execute_command(add_cmd, None)
                    print(name)
    
            game_runner.execute_command("start", current_player)
            game_runner.run_game()
    
if __name__ == '__main__':
    main()
    
