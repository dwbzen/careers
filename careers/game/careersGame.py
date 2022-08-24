'''
Created on Aug 6, 2022

@author: don_bacon
'''

from careers.environment import Environment
from game.player import Player
import json, random
from datetime import datetime
from pathlib import Path
from game.opportunityCardDeck import OpportunityCardDeck
from game.experienceCardDeck import ExperienceCardDeck
from game.borderSquare import BorderSquare
from game.occupationSquare import OccupationSquare
from game.gameState import GameState
from game.occupation import Occupation
from plotly.validators.pointcloud.marker import border

class CareersGame(object):
    """
    Represents a Careers Game instance.
        The CareersGame model class has instances of all the components used in game play:
        Opportunity and Experience card decks, the game board, parameters for a given edition, occupations, players, and the game state.
        
    """

    def __init__(self, edition_name, total_points):
        """CareersGame Constructor
            Arguments:
                edition_name - the name of the edition to create. This must be a key in editions.json file.
                total_points - total number of points in the success formula.
            Raises:
                ValueError if there is no such edition
        """
        self._edition_name = edition_name
        self._env = Environment.get_environment()
        self._resource_folder = self._env.get_resource_folder()     # base resource folder
        #
        # validate the Edition
        #
        fp = open(self._resource_folder + "/editions.json", "r")
        jtxt = fp.read()
        editions_txt = json.loads(jtxt)
        self._editions = editions_txt['editions']   # list of editions
        if edition_name in self._editions:
            self._edition = editions_txt[edition_name]
        else: raise ValueError(f"No such edition {edition_name}")
        fp.close()
        #
        # load game parameters, layout and occupations
        #
        self._load_game_configuration()
 
        #
        # create the Opportunity and Experience card decks
        #
        self._create_opportunity_deck()
        self._create_experience_deck()
        self._college_degrees =  self._load_college_degrees()  # dict with keys: degreePrograms (list), maxDegrees (int), degreeNames (list)
        #
        # load the game board
        #
        self._occupation_entrance_squares = {}     # dictionary of BorderSquare that are type "occupation_entrance_square" indexed by name
        self._travel_squares = []                  # list of BorderSquare that are type "travel_square"
        self._game_board = self._create_game_board()   # list of BorderSquare
        self._game_type = 'points'  # 'points' or 'timed' (which is not yet supported)

        #
        # create & initialize the GameState which includes a list of Players
        #
        self._game_state = GameState(total_points)
        #
        # create a unique ID for this game, used for logging
        #
        today = datetime.now()
        self._gameId = '{0:d}{1:02d}{2:02d}_{3:02d}{4:02d}_{5:04d}'.format(today.year, today.month, today.day,today.hour, today.minute, random.randint(1000,9999))
        
    def _load_game_configuration(self):
        """Loads the game parameters and occupations JSON files for this edition.
        
        """
        fp = open(self._resource_folder + "/gameParameters_" + self._edition_name + ".json", "r")
        jtxt = fp.read()
        self._game_parameters = json.loads(jtxt)
        fp.close()

        fp = open(self._resource_folder + "/occupations_" + self._edition_name + ".json", "r")
        jtxt = fp.read()
        occupations_dict = json.loads(jtxt)
        self._occupation_names = occupations_dict['occupations']
        fp.close()
        
        # load the individual occupation files
        self._occupations = self.load_occupations()     # dictionary of Occupation instances keyed by name

        
    def _create_opportunity_deck(self):
        self._opportunities = OpportunityCardDeck(self._resource_folder, self._edition_name)
    
    def _create_experience_deck(self):
        self._experience_cards = ExperienceCardDeck(self._resource_folder, self._edition_name)
        
    def _create_game_board(self):
        fp = open(self._resource_folder + "/gameLayout_" + self._edition_name + ".json", "r")
        self._game_board_dict = json.loads(fp.read())
        self._game_layout = self._game_board_dict['layout']
        self._game_layout_dimensions = self._game_board_dict['dimensions']
        self._game_board_size = self._game_layout_dimensions['size']
        game_board = list()
        for border_square_dict in self._game_layout:
            border_square = BorderSquare(border_square_dict)
            game_board.append(border_square)
            
            if border_square.square_type == "occupation_entrance_square":
                self._occupation_entrance_squares[border_square.name] = border_square
                
            if border_square.square_type == "travel_square":
                self._travel_squares.append(border)
        return game_board

    def load_occupations(self) -> dict:
        """Loads individual occupation JSON files for this edition.
            Arguments: occupation_list - a list of occupation names
            Returns: a dict with the occupation name as the key and contents
                of the corresponding occupation JSON file (as a dict) as the value.
                If the occupation JSON file doesn't exist, the value is None.
            Note: the filename is the occupation name + "_" + the edition_name + ".json"
                The file path is the resource_folder set in the Environment
        """
        occupations = dict()
        for name in self._occupation_names:
            filepath = self._resource_folder + "/" + name + "_" + self._edition_name + ".json"
            p = Path(filepath)
            if p.exists():
                fp = open(filepath, "r")
                occupation_dict = json.loads(fp.read())
                # create an Occupation object for this occupation
                occupation = Occupation(occupation_dict)
                occupations[name] = occupation
            else:
                occupations[name] = None
        return occupations

    
    def _load_college_degrees(self):
        fp = open(self._resource_folder + "/collegeDegrees_" + self._edition_name + ".json", "r")
        degrees = json.loads(fp.read())
        return degrees
    
    @property
    def edition(self):
        return self._edition
    
    @property
    def edition_name(self):
        return self._edition_name
    
    @property
    def game_layout(self):
        return self._game_layout
    
    @property
    def game_layout_dimensions(self):
        """size (number of squares), sides (4-element list of #squares/side)
        """
        return self._game_layout_dimensions
    
    @property
    def game_board_size(self):      # this cannot be set
        return self._game_board_size
    
    @property
    def game_parameters(self):
        return self._game_parameters
    
    @property
    def game_state(self):
        return self._game_state
    
    @property
    def gameId(self):
        return self._gameId
    
    def game_type(self):
        return self._game_type
    
    @property
    def occupation_names(self) ->list:
        """List of occupation names (keys) for this edition
        """
        return self._occupation_names
    
    @property
    def occupations(self) -> dict:
        """Dictionary of Occupation instances keyed by occupation name
        """
        return self._occupations
    
    @property
    def occupation_entrance_squares(self) -> dict:
        return self._occupation_entrance_squares
    
    @property
    def travel_squares(self) -> list:
        return self._travel_squares
    
    @property
    def opportunities(self):
        return self._opportunities
    
    @property
    def experience_cards(self):
        return self._experience_cards
    
    @property
    def game_board(self):
        return self._game_board
    
    def add_player(self, aplayer:Player):
        self.game_state.add_player(aplayer)
    
    def complete_player_move(self):
        """Completes the move of the current player and determines if there's a winner and returns winning_player.
            If so winning_player is set. Otherise, current_player and current_player_number advanced to the next player.
            Returns: winning_player (Player instance) or None
        
        """
        winner = None
        if self.is_game_complete():       # sets winning_player if True
            winner = self.winning_player
        else:
            self.next_player_number()
        return winner
            
    
    def is_game_complete(self):
        """Iterates over the players to see who, if anyone, has won.
            Returns: True if there's a winner, else False.
                    sets self.winning_player to the Player who won.
            NOTE - returns the first winning player if there happens to be more than 1.
            To prevent this from happening, this should be called at the end of each player's turn.
        """
        completed = False
        for p in self.players:
            if p.is_complete():
                self._winning_player = p
                completed = True
                break
        return completed
    
    def start_game(self):
        """
        Initializes game state and starts the game
        TODO
        """
        pass
    
    def complete_turn(self):
        """Completes the turn of the current_player
        
        """
        pass
    
if __name__ == '__main__':

    game = CareersGame('Hi-Tech')
    print(game.occupation_list)
    
    
