'''
Created on May 23, 2023

@author: don_bacon
'''

from game.plugins.plugin import Plugin

class Careers_Randomizer(Plugin):
    '''
    Implements the optional Randomizer feature for selecting mandatory occupation(s) and degree(s).
    '''


    def __init__(self):
        '''
        Constructor
        '''
        super().__init__("All") 
    
    