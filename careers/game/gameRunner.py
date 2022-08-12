'''
Created on Aug 12, 2022

@author: don_bacon
'''

from game.careersGame import CareersGame

class GameRunner(object):
    """A command-line text version of Careers game play used for testing.
    
    """


    def __init__(self, params):
        """
        Constructor
        """
        self.game = CareersGame('Hi-Tech')
