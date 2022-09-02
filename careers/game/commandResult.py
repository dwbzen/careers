'''
Created on Aug 21, 2022

@author: don_bacon
'''
from game.careersObject import CareersObject
from game.boardLocation import BoardLocation

class CommandResult(CareersObject):
    """Encapsulates the result of a command executed by a game square or the CareersGameEngine
    
    """
    SUCCESS = 0         # Successful result
    ERROR = 1           # There was an error. message contains the error message
    TERMINATE = 2       # terminate the game
    EXECUTE_NEXT = 3    # successful, and execute the next_action for the current player

    def __init__(self, return_code:int, message:str, done_flag:bool, next_action=None, board_location:BoardLocation=None, exception:Exception=None):
        """Constructor, baby.
            Arguments:
                return_code - integer return code:
                    SUCCESS = 0  Successful result
                    ERROR = 1  There was an error. message contains the error message
                    TERMINATE = 2  terminate the game
                    EXECUTE_NEXT = 3  success, and execute the next_action for the current player
                message - a message string to be displayed to the player
                done_flag - if  True, this player's turn is completed, False otherwise.
                next_action - next action to perform for this player, default is None. 
                        This will be in the format of an executable command, for example "roll" as this is
                        passed to the game engine execute_command() method.
                board_location - the board location (of the current player) after the command is executed.
                exception - the Exception instance if the command raised an exception, default is None
        """
        self._return_code = return_code
        self._message = message
        self._done_flag = done_flag
        self._exception = exception
        self._next_action = next_action
        self._board_location = board_location
    
    @property
    def return_code(self):
        return self._return_code
    @return_code.setter
    def return_code(self, value):
        self._return_code = value
    
    @property
    def message(self):
        return self._message
    @message.setter
    def message(self, amessage):
        self._message = amessage
    
    @property
    def done_flag(self):
        return self._done_flag
    @done_flag.setter
    def done_flag(self, value):
        self._done_flag = value
    
    @property
    def exception(self):
        return self._exception
    @exception.setter
    def exception(self, value):
        self._exception = value
        
    @property
    def next_action(self):
        return self._next_action
    @next_action.setter
    def next_action(self, value):
        self._next_action = value
        
    @property
    def board_location(self):
        return self._board_location
    @board_location.setter
    def board_location(self, value):
        self._board_location = value
        
    def to_JSON(self):
        jstr = f'{{\n  "return_code" : "{self.return_code}",\n  "done_flag" : "{self.done_flag}",\n  "message" : "{self.message}",\n'
        if self.next_action is not None:
            jstr += f'  "next_action" : "{self.next_action}",\n'
        if self.exception is not None:
            jstr += f'  "exception : "{str(self.exception)}",\n'
        if self.board_location is not None:
            bl = self.board_location.to_JSON()
            jstr += f'"board_location" : {bl}\n'
        jstr += "}"
        return jstr
        