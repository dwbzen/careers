'''
Created on Aug 12, 2022

@author: don_bacon
'''

from game.specialProcessing import SpecialProcessing

class BorderSquare(object):
    """Encapsulates a Careers game border (non-occupation) square.
    Border squares are numbered consecutively starting with 0 (Payday by convention).
    They also have a name which may not be unique. For example, there are 12 squares named "Opportunity"
    The border square "type" is enumerated in the game layout JSON as "types"
    """


    def __init__(self, border_square_txt):
        """
        Constructor
        """
        self._text = None
        self._special_processing = None
        self._number = border_square_txt['number']
        self._name = border_square_txt['name']
        self._square_type = border_square_txt['type']
        if 'text' in border_square_txt:
            self._text = border_square_txt['text']
        if 'specialProcessing' in border_square_txt:
            self._special_processing_txt = border_square_txt['specialProcessing']
            self._special_processing = SpecialProcessing(self._special_processing_txt, "border")
    
    @property
    def number(self):
        return self._number
    
    @property
    def name(self):
        return self._name
    
    @property
    def special_processing(self):
        return self._special_processing
    
    