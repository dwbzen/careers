'''
Created on Aug 9, 2022

@author: don_bacon
'''
import json
from pathlib import Path
from game.gameUtils import GameUtils

class CardDeck(object):
    """Abstract class representing a deck of game cards a player draws or is given.
    
    """


    def __init__(self, resource_path, deck_name, edition_name):
        '''
        Constructor
        '''
        self._resource_path = resource_path
        self._deck_name = deck_name         # "opportunityCards" or "experienceCards" for example
        self._edition_name = edition_name
        self._cards_content = self.load_cards(resource_path, deck_name, edition_name)
        self._type_list = self._cards_content['types_list']
        self._help = self._cards_content['Help']
        self._card_types = self._cards_content['types']
        self._cards = self._cards_content['cards']
        
        self._deck = []

        self._cards_index = []
        self._size = self.create_card_deck()
        self._cards_index = GameUtils.shuffle(self._size)
        self._next_index = 0
        
    def shuffle(self):
        self._cards_index = GameUtils.shuffle(self._size)
        
    @property
    def size(self):
        return self._size
    
    @property
    def next_index(self):
        return self._next_index
    
    @next_index.setter
    def next_index(self, value):
        self._next_index = value
    
    def draw(self):
        """Draw a card from the deck. If no cards remaining, re-shuffle and reset the next_index
        
        """
        next_card = None
        if self.next_index < self.size:    # draw the next card
            nxt = self._cards_index[self.next_index]
            next_card = self._deck[nxt]
            self.next_index = self.next_index + 1
        else:
            self.next_index = 0
            self.shuffle()
            return self.draw()
        return next_card
    
    def draw_cards(self, ncards:int):
        #
        # override in derived class
        #
        return None
    
    def load_cards(self, path, name, edition_name):
        """Loads the specified card deck JSON file. This assumes the resulting structure is a dict
            with keys: "Help", "type_list", "types", and "cards"
            Arguments:
                path - JSON file path
                name - the card deck name, for example "opportunityCards"
                edition_name
            Returns:
                the JSON content as a dict
        """
        cards = dict()
        filepath = f'{path}/{name}_{edition_name}.json'
        p = Path(filepath)
        if p.exists():
            fp = open(filepath, "r")
            cards = json.loads(fp.read())
        return cards
    
    def create_card_deck(self):
        count = 0
        for card_spec in self._cards:
            qty = card_spec['quantity']
            count += qty
            self.save_card(card_spec, qty)
        return count
        
    def save_card(self, card_spec, qty):
        """Saves a single Opportunity or Experience card.
        
        Abstract method - Override in concrete class.
        """
        pass
    
    
    