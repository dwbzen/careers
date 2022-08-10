'''
Created on Aug 9, 2022

@author: don_bacon
'''

class OpportunityCard(object):
    """
    Represents a single Opportunity card
    """

    def __init__(self, opportunity_type, border_square=None, text="", expenses_paid=False, double_happiness=False):
        """Constructor
            Arguments:
                opp_type - the OpportunityType of this card
                border_square - the "name" of the corresponding border square if there is a destination, otherwise None
                text - the Opportunity card text
                expenses_paid - Applies to OpportunityType.OCCUPATION: True if the player can enter for free.
                double_happiness - Applies to OpportunityType.OCCUPATION: True if happiness point values are doubled.
        """
        self._opportunity_type = opportunity_type
        if border_square == "":
            self._border_square = None
        else:
            self._border_square = border_square
        self._text = text
        self._expenses_paid = expenses_paid
        self._double_happiness = double_happiness
        
    @property
    def opportunity_type(self) ->str:
        return self._opportunity_type
    
    @opportunity_type.setter
    def opportunity_type(self, ctype:str):
        self._opportunity_type = ctype
    
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

        
    