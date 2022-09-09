'''
Created on Aug 13, 2022

@author: don_bacon
'''

import jsonpickle
class CareersObject(object):
    """Base class for object that have a JSON representation.
    """

    def __init__(self, params):
        '''
        Constructor
        '''
        pass
    
    def to_JSON(self):
        """Returns my JSON representation. Abstract class.
        """
        return None
    
    def json_pickle(self):
        """A complete JSON representation of this object using jsonpickle.
        """
        return jsonpickle.encode(self, indent=2)
        
    def __repr__(self):
        return self.json_pickle()
    
    def __str__(self):
        return self.to_JSON()
    