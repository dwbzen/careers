'''
Created on Aug 12, 2022

@author: don_bacon
'''


class SpecialProcessing(object):
    """Encapsulates the "specialProcessing" section of a border square or occupation square, or an Opportunity card directive.
        This is only a model class. The actual processing is done by CareersGameEngine.
    """
    
    border_types = ["payday", "opportunity", "payTax", "enterOccupation", "enterCollege", "buyHearts", "buyStars", "buyExperience",\
                    "hospital", "unemployment", "buyInsurance", "gamble" ]

    occupation_types = ["loseNextTurn", "travelShortcut", "travelOccupation", "cashLossOrUnemployment",\
                         "salaryIncrease", "salaryCut", "bonus", "favors", "backstab", "fameLoss", "hapinessLoss"]
    
    common_types = ["travelBorder", "cashLoss", "extraTurn"]
    
    all_types = border_types + occupation_types + common_types

    def __init__(self, special_processing_dict:str, square_type:str):
        """Constructor
            Arguments:
                special_processing_dict - the JSON specialProcessing section of a border or occupation square as a dictionary
                square_type - "occupation" or "border"
        """
        self._special_processing_dict = special_processing_dict
        #
        # mandatory elements
        #
        self._square_type = square_type     # "occupation" or "border"
        self._processing_type = special_processing_dict["type"]     # must be one of the above types
        #
        # optional elements which are type-dependent
        # an 'amount' can be a numeric type (int or float), a string or a dictionary
        #
        self._amount = 0            # a discrete money amount which may be salary or cash depending on type
        self._amount_dict = None
        self._amount_str = ""
        amt = special_processing_dict.get('amount', 0)    # 'amount' is optional
        if isinstance(amt, int) or isinstance(amt, float):
            self._amount = amt
        elif isinstance(amt, str):
            self._amount_str = amt
        else:
            self._amount_dict = amt    # how a money amount is calculated
        
        self._dice = special_processing_dict.get('dice', 0)   # number of dice used to calculate some amount
        self._penalty = special_processing_dict.get('penalty', 0)           # a loss quantity (hearts or stars)
        self._limit = special_processing_dict.get('limit', None)          # a limiting factor, usually "salary" (in 1000s)
        
        # square number to advance to, relative to the overall game layout or occupation
        self._next_square = special_processing_dict.get('next_square', None)    

        self._destination = special_processing_dict.get('destinationOccupation', None)  # the name of a destination occupation
        self._percent = special_processing_dict.get('percent', 0)       # a percent amount of salary or cash depending on type
    
    @property
    def square_type(self):
        return self._square_type
    
    @property
    def processing_type(self):
        return self._processing_type
    
    @property
    def amount(self):
        return self._amount
    
    @property
    def amount_dict(self):
        return self._amount_dict
    
    @property
    def amount_str(self):
        return self._amount_str
    
    @property
    def destination(self):
        return self._destination
    
    @property
    def dice(self):
        return self._dice
    
    @property
    def limit(self):
        return self._limit
    
    @property
    def next_square(self):
        return self._next_square
    
    @property
    def penalty(self):
        return self._penalty
    
    @property
    def percent(self):
        return self._percent
    
    def __str__(self):
        return self._special_processing_dict
