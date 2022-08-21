'''
Created on Aug 21, 2022

@author: don_bacon
'''

class CommandResult(object):
    """Encapsulates the result of a command executed by a game square or the CareersGameEngine
    
    """
    SUCCESS = 0         # Successful result
    ERROR = 1           # There was an error. message contains the error message
    TERMINATE = 2       # terminate the game

    def __init__(self, return_code:int, message:str, done_flag:bool, exception:Exception=None):
        """Constructor, baby.
        
        """
        self._return_code = return_code
        self._message = message
        self._done_flag = done_flag
        self._exception = exception
    
    @property
    def return_code(self):
        return self._return_code
    @property
    def message(self):
        return self._message
    @property
    def done_flag(self):
        return self._done_flag
    @property
    def exception(self):
        return self._exception
    @exception.setter
    def exception(self, value):
        self._exception = value

    
        