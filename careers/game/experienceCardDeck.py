'''
Created on Aug 9, 2022

@author: don_bacon
'''

from game.cardDeck import CardDeck
from game.experienceCard import ExperienceCard
from typing import List

class ExperienceCardDeck(CardDeck):
    """The deck of Experience Cards used in game play.
    
    """

    def __init__(self, resource_path, edition_name):
        '''
        Constructor
        '''
        super().__init__(resource_path, "experienceCards", edition_name)    # loads the card deck
        
    def save_card(self, card_spec, qty):
        """Appends n-instances of a single Experience card to the card deck.
            Arguments: card_spec - the JSON experience card content as a dict
            
        card_spec includes "quantity" tag that specifies the number of this cards that appear in the deck.

        """
        number = card_spec['number']
        for ncard in range(1, qty+1):
            experience_card = ExperienceCard(number, ncard, card_spec['card_type'], card_spec['spaces'])
            experience_card.value = self.card_values[card_spec['card_type']]
            self._deck.append(experience_card)
    
    def draw_cards(self, ncards:int) -> List[ExperienceCard]:
        assert(ncards > 0)
        card_list = []
        for i in range(ncards):
            card_list.append(self.draw())
        return card_list