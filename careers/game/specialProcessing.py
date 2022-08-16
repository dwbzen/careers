'''
Created on Aug 12, 2022

@author: don_bacon
'''


class SpecialProcessing(object):
    """Encapsulates the "specialProcessing" section of a border square or occupation square.
    
    """
    
    border_types = ["payday", "opportunity", "payTax", "enterOccupation", "enterCollege"]

    occupation_types = ["loseNextTurn", "travelShortcut", "travelOccupation", "cashLossOrUnemployment", "salaryIncrease", "salaryCut", "bonus", "favors", "backstab"]
    
    common_types = ["travelBorder", "cashLoss"]

    def __init__(self, special_processing_dict:str, square_type:str):
        """Constructor
            Arguments:
                special_processing_txt - the JSON specialProcessing section of a border or occupation square as a dict
                square_type - "occupation" or "border"
        """
        self._special_processing_dict = special_processing_dict
        #
        # mandatory elements
        #
        self._square_type = square_type
        self._processing_type = special_processing_dict["type"]
        #
        # optional elements which are type-dependent
        #
    
        self._amount_calc = None    # how a money amount is calculated
        self._amount = 0            # a discrete money amount which may be salary or cash depending on type
        
        self._dice = special_processing_dict.get('dice', 0)   # number of dice used to calculate some amount
        
        # square number to advance to, relative to the overall game layout or occupation
        self._next_square = special_processing_dict.get('next_square', None)    
        
        if 'amount' in special_processing_dict:
            amt = special_processing_dict['amount']
            if type(amt) is str:
                self._amount_calc = amt
            else:
                self._amount = amt

        self._destination = special_processing_dict.get('destinationOccupation', None)  # the name of a destination occupation
        self._percent = special_processing_dict.get('percent', 0)       # a percent amount of salary or cash depending on type
    
    
    def __str__(self):
        return self._special_processing_txt
