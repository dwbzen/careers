'''
Created on Aug 9, 2022

@author: don_bacon
'''

from game.cardDeck import CardDeck
from game.experienceCard import ExperienceCard

class ExperienceCardDeck(CardDeck):
    '''
    classdocs
    '''

    def __init__(self, resource_path, edition_name):
        '''
        Constructor
        '''
        super().__init__(resource_path, "experienceCards", edition_name)    # loads the card deck
        
    def save_card(self, card_spec, qty):
        """Save a single Experience card.
        
        """
        for ncards in range(1, qty+1):
            experience_card = ExperienceCard(card_spec['type'], card_spec['spaces'])
            self._deck.append(experience_card)
    