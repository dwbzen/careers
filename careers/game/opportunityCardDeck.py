'''
Created on Aug 9, 2022

@author: don_bacon
'''

from game.cardDeck import CardDeck
from game.opportunityCard import OpportunityCard,OpportunityType

class OpportunityCardDeck(CardDeck):
    """The deck of Opportunity Cards used in game play.
    
    """

    def __init__(self, resource_path, edition_name):
        '''
        Constructor
        '''
        super().__init__(resource_path, "opportunityCards", edition_name)    # loads the card deck
        self._opportunity_types = list(OpportunityType)  # ["occupation", "occupation_choice", "border_square", "border_square_choice", "action", "travel", "opportunity" ]

        
    def save_card(self, card_spec:dict, qty):
        """Appends n-instances of a single Opportunity card to the card deck.
            Arguments: card_spec - the JSON opportunity card content as a dict
            
        card_spec includes:
            "number" - the unique card number. Cards having the same number are identical.
            "quantity" - specifies the number of this card that appear in the deck.
        
        """
        number = card_spec['number']
        destination = card_spec['destination']
        ctype = card_spec['card_type']
        expenses_paid = card_spec.get('expenses_paid', 0) == 1
        double_happiness = card_spec.get('double_happiness', 0) == 1

        for ncard in range(1, qty+1):
            action_type = card_spec.get("action_type", None)
            opportunity_card = OpportunityCard(ctype, number, ncard, destination, card_spec['text'], expenses_paid, double_happiness, action_type)
            self._deck.append(opportunity_card)

    @property
    def opportunity_types(self):
        return self._opportunity_types

