'''
Created on Aug 6, 2022

@author: don_bacon
'''

from careers.environment import Environment
from careers.game import Player, SuccessFormula
import json
from pathlib import Path

class CareersGame(object):
    """
    Represents a Careers Game instance.
    """

    def __init__(self, edition_name):
        """CareersGame Constructor
        
        """
        self._edition_name = edition_name
        self._env = Environment.get_environment()
        self._resource_folder = self._env.get_resource_folder()     # base resource folder
        #
        # validate the Edition
        #
        fp = open(self._resource_folder + "/editions.json", "r")
        jtxt = fp.read()
        self._editions = json.loads(jtxt)
        if edition_name in self._editions[edition_name]:
            self._edition = self._editions[edition_name]
        else: raise ValueError(f"No such edition {edition_name}")
        fp.close()
        #
        # load game parameters, layout and occupations
        #
        self._load_game_configuration()
        self._players = []   # list of Player
        #
        # create the Opportunity and Experience card decks
        #
        self._create_opportunity_deck()
        self._create_experience_deck()
        
    def _load_game_configuration(self):
        """Loads the game parameters, layout and occupations JSON files for this edition.
        
        """
        fp = open(self._resource_folder + "/gameParameters_" + self._edition_name + ".json", "r")
        jtxt = fp.read()
        self._game_parameters = json.loads(jtxt)
        fp.close()
        fp = open(self._resource_folder + "/gameLayout_" + self._edition_name + ".json", "r")
        jtxt = fp.read()
        self._game_layout = json.loads(jtxt)
        fp.close()
        fp = open(self._resource_folder + "/occupations_" + self._edition_name + ".json", "r")
        jtxt = fp.read()
        occupations = json.loads(jtxt)
        self._occupation_list = occupations['occupations']
        fp.close()
        
        self._occupations = CareersGame.load_occupations(self._occupation_list)
        self._opportunities = CareersGame.load_opportunity_cards(self._edition_name)
        self._experience_cards = CareersGame.load_experience_cards(self._edition_name)
    
    @staticmethod
    def load_occupations(occupation_list : list) -> dict:
        """Loads individual occupation JSON files for this edition.
            Arguments: occupation_list - a list of occupation names
            Returns: a dict with the occupation name as the key and contents
                of the corresponding occupation JSON file as the value.
                If the occupation JSON file doesn't exist, the value is None.
        """
        occupations = dict()
        for name in occupation_list:
            filepath = self._resource_folder + "/" + name + self._edition_name + ".json"
            p = Path(filepath)
            if p.exists():
                fp = open(filepath, "r")
                occupation = json.loads(fp.read())
                occupations[name] = occupation
            else:
                occupations[name] = None
        return occupations
    
    @staticmethod
    def load_opportunity_cards(edition_name) -> dict:
        cards = dict()
        filepath = self._resource_folder + "/opportunityCards_" + edition_name + ".json"
        p = Path(filepath)
        if p.exists():
            fp = open(filepath, "r")
            cards = json.loads(fp.read())
        return cards
    
    @staticmethod
    def load_experience_cards(edition_name) -> dict:
        cards = dict()
        filepath = self._resource_folder + "/experienceCards_" + edition_name + ".json"
        p = Path(filepath)
        if p.exists():
            fp = open(filepath, "r")
            cards = json.loads(fp.read())
        return cards
    
    def _create_opportunity_deck(self):
        pass
    
    def _create_experience_deck(self):
        pass
    
    @property
    def edition(self):
        return self._edition
    
    @property
    def game_layout(self):
        return self._game_layout
    
    @property
    def game_parameters(self):
        return self._game_parameters
    
    @property
    def occupation_list(self):
        """List of occupation handles (keys) for this edition
        
        """
        return self._occupation_list
    
    @property
    def occupations(self):
        return self._occupations
    
    @property
    def opportunities(self):
        return self._opportunities
    
    @property
    def experience_cards(self):
        return self._experience_cards
    
    @property
    def players(self):
        return self._players
    
    def add_player(self, aplayer):
        self.players.append(aplayer)
    
    def start_game(self):
        """
        Initializes game state and starts the game
        TODO
        """
        pass
    
if __name__ == '__main__':
    player = Player(name='Don', initials='DWB')
    sf = SuccessFormula(stars=40, hearts=10, cash=50)
    player.success_formula = sf
    game = CareersGame('Hi-Tech')
    game.add_player(player)

