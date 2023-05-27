'''
Created on May 23, 2023

@author: don_bacon
'''
from game.plugins.plugin import Plugin

class Careers_HiTech_Rules(Plugin):
    '''
    Implement mandatory rules for the Hi-Tech edition
    '''


    def __init__(self):
        '''
        Constructor
        '''
        super().__init__("HiTech")

