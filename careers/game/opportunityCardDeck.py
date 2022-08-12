'''
Created on Aug 9, 2022

@author: don_bacon
'''

from game.cardDeck import CardDeck
from game.opportunityCard import OpportunityCard

class OpportunityCardDeck(CardDeck):
    """The deck of Opportunity Cards used in game play.
    
    """

    def __init__(self, resource_path, edition_name):
        '''
        Constructor
        '''
        super().__init__(resource_path, "opportunityCards", edition_name)    # loads the card deck
        
    def save_card(self, card_spec, qty):
        """Appends n-instances of a single Opportunity card to the card deck.
            Arguments: card_spec - the JSON opportunity card content as a dict
            
        card_spec includes "quantity" tag that specifies the number of this cards that appear in the deck.
        
        """
        border_square = card_spec['border_square']
        ctype = card_spec['type']
        expenses_paid = card_spec['expenses_paid'] == 1
        double_happiness = card_spec['double_happiness'] == 1
        for ncards in range(1, qty+1):
            opportunity_card = OpportunityCard(ctype, border_square, card_spec['text'], expenses_paid, double_happiness)
            self._deck.append(opportunity_card)

        