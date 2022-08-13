'''
Created on Aug 12, 2022

@author: don_bacon
'''


class SpecialProcessing(object):
    """Encapsulates the "specialProcessing" section of a border square or occupation square.
    
    """

    def __init__(self, special_processing_txt:str, square_type:str):
        """Constructor
            Arguments:
                special_processing_txt - the JSON specialProcessing section of a border or occupation square
                square_type - "occupation" or "border"
        """
        self._special_processing_txt = special_processing_txt
        #
        # mandatory elements
        #
        self._square_type = square_type
        self._processing_type = special_processing_txt["type"]
        #
        # optional elements which are type-dependent
        #
        self._dice = 0      # number of dice used to calculate some amount
        self._next_square = None    # square number to advance to, relative to the overall game layout or occupation
        self._amount_calc = None    # how a money amount is calculated
        self._amount = 0            # a discrete money amount which may be salary or cash depending on type
        self._destination = None    # the name of a destination occupation or border square
        
        if 'dice' in special_processing_txt:
            self._dice = special_processing_txt['dice']
        if 'next_square' in special_processing_txt:
            self._next_square = special_processing_txt['next_square']
        if 'amount' in special_processing_txt:
            amt = special_processing_txt['amount']
            if type(amt) is str:
                self._amount_calc = amt
            else:
                self._amount = amt
        if 'destinationOccupation' in special_processing_txt:
            self._destination = special_processing_txt['destinationOccupation']
    
    
    def __str__(self):
        return self._special_processing_txt
