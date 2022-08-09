'''
Created on Aug 9, 2022

@author: don_bacon
'''

from careers.game import OpportunityType

class OpportunityCard(object):
    """
    Represents a single Opportunity card
    """

    def __init__(self, atype=OpportunityType.OCCUPATION, border_square=None, text="", expenses_paid=False, double_happiness=False):
        """
        Constructor
        """
        self._card_type = atype
        self._border_square = border_square
        self._text = text
        self._expenses_paid = expenses_paid
        self._double_happiness = double_happiness
        
    @property
    def card_type(self) -> OpportunityType:
        return self._card_type
    
    @card_type.setter
    def card_type(self, ctype:OpportunityType):
        self._card_type = ctype
    
    @property
    def border_square(self):
        return self._border_square
    
    @border_square.setter
    def border_square(self, bs):
        self._border_square = bs
    
    @property
    def text(self):
        return self._text
    
    @text.setter
    def text(self, text):
        self._text = text
    
    @property
    def expenses_paid(self):
        return self._expenses_paid
    
    @expenses_paid.setter
    def expenses_paid(self, ep):
        self._expenses_paid = ep
    
    @property
    def double_happiness(self):
        return self._double_happiness
    
    @double_happiness.setter
    def double_happiness(self, dh):
        self._double_happiness = dh
    
    