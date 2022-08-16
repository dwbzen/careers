'''
Created on Aug 14, 2022

@author: don_bacon
'''

from careers.game import CareersGame
from game.player import  Player
from datetime import datetime

class CareersGameEngine(object):
    """CareersGameEngine executes the action(s) associated with each player's turn.
    
    """

    def __init__(self, careersGame:CareersGame):
        '''
        Constructor
        '''
        self._careersGame = careersGame
        self._game_state = self._careersGame.game_state
        self._trace = True         # traces the action by describing each step and logs to a file
        self._logfile_name = "careersLog_" + careersGame.edition_name
        self._logfile_path = "/data/log"    # TODO put in Environment
        self._fp = None     # log file open channel
        self._start_date_time = datetime.now()
        self._gameId = careersGame.gameId
    
    @property
    def fp(self):
        return self._fp
    
    @fp.setter
    def fp(self, value):
        self._fp = value
    
    @property
    def logfile_name(self):
        return self._logfile_name
    
    @property
    def logfile_path(self):
        return self._logfile_path
    
    @property
    def gameId(self):
        return self._gameId
    
    @property
    def trace(self):
        return self._trace
    
    @trace.setter
    def trace(self, value):
        self._trace = value
        
    @property
    def game_state(self):
        return self._game_state
    
    def get_datetime(self) -> str:
        now = datetime.today()
        return '{0:d}{1:02d}{2:02d}_{3:02d}{4:02d}'.format(now.year, now.month, now.day, now.hour, now.minute)
    
    def log(self, message):
        msg = self.get_datetime() + f'  {message}\n'
        self.fp.write(msg)
        if self.trace:
            print(msg)
    
    def start(self):
        self.fp = open(self.logfile_path + "/" + self.logfile_name + "_" + self.gameId + ".log", "w")
        self.log("Starting game: " + self.gameId)
    
    def end(self):
        self.log("Ending game: " + self.gameId)
        self.fp.close()
    
    def execute_command(self, command:str, args:list, player:Player):
        pass
    

