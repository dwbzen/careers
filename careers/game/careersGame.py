'''
Created on Aug 6, 2022

@author: don_bacon
'''

from careers.environment import Environment
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
      
    
    def start_game(self):
        """
        Initializes game state and starts the game
        """
        pass
    
    