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
from game.gameState import GameState
from game.occupation import Occupation
from game.gameBoard import GameBoard
from game.borderSquare import BorderSquare
from game.careersObject import CareersObject
from threading import Lock

class CareersGame(CareersObject):
    """
    Represents a Careers Game instance.
        The CareersGame model class has instances of all the components used in game play:
        Opportunity and Experience card decks, the game board, parameters for a given edition, occupations, players, and the game state.
        
    """
    _lock = Lock()
    
    def __init__(self, edition_name,  master_id, total_points, game_id, game_type="points"):
        """CareersGame Constructor
            Arguments:
                master_id - An ID that uniquely identifies the game's creator - a.k.a the game master
                edition_name - the name of the edition to create. This must be a key in editions.json file.
                total_points - total number of points in the success formula or in a timed game, the number of minutes.
                game_id - a Globally Unique Identifier for this game (guid). If not provided, one is generated from the current date/time.
            Raises:
                ValueError if there is no such edition
            Saved games are indexed by master_id. This is the primary search key used to search for saved games.
            It's the responsibility of the front end GUI to provide this.
        """
        self._master_id = master_id
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
        self._game_board = self._create_game_board()   # GameBoard instance
        self._game_type = game_type  # 'points' or 'timed' (which is not yet supported)

        #
        # create & initialize the GameState which includes a list of Players
        #
        self._game_state = GameState(total_points, self._game_type)
        #
        # create a unique ID for this game, used for logging
        #
        self._gameId = game_id
        #
        # if a gameId is not provided, create one
        #
        if game_id is None:
            self._gameId = self._create_game_id()
        
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

    def _create_game_id(self):
        """Create a unique game id (guid) for this game.
            This method acquires a lock to insure uniqueness in a multi-process/web environment.
            Format is based on current date and time, for example 20220908-140952-973406-27191
        """
        CareersGame._lock.acquire()
        today = datetime.now()
        gid =  '{0:d}{1:02d}{2:02d}-{3:02d}{4:02d}{5:02d}-{6:06d}-{7:05d}'.format(today.year, today.month, today.day, today.hour, today.minute, today.second, today.microsecond, random.randint(10000,99999))
        CareersGame._lock.release()
        return gid
    
    def _create_opportunity_deck(self):
        self._opportunities = OpportunityCardDeck(self._resource_folder, self._edition_name)
    
    def _create_experience_deck(self):
        self._experience_cards = ExperienceCardDeck(self._resource_folder, self._edition_name)
        
    def _create_game_board(self):
        game_layout_filename = self._resource_folder + "/gameLayout_" + self._edition_name + ".json"
        game_board = GameBoard(game_layout_filename, game=self)
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
    def game_board(self) -> GameBoard:
        return self._game_board
    
    def get_border_square(self, num) -> BorderSquare:
        """Convenience method to get a BorderSquare instance from the GameBoard
        """
        return self._game_board.get_square(num)
    
    def get_game_layout_dimensions(self):
        """size (number of squares), sides (4-element list of #squares/side)
        """
        return self.game_board.game_layout_dimensions
    

    def get_game_board_size(self):
        return self.game_board.game_board_size
    
    
    @property
    def game_parameters(self):
        return self._game_parameters
    
    @property
    def game_state(self):
        return self._game_state
    
    @property
    def gameId(self):
        return self._gameId
    
    @property
    def master_id(self):
        return self._master_id
    
    @master_id.setter
    def master_id(self, value):
        self._master_id = value
    
    @property
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
    

    def get_occupation_entrance_squares(self) -> dict:
        return self.game_board.occupation_entrance_squares
    
    def get_travel_squares(self) -> list:
        return self.game_board.travel_squares
    
    def get_corner_squares(self) -> dict:
        return self.game_board.corner_squares
    
    @property
    def opportunities(self):
        return self._opportunities
    
    @property
    def experience_cards(self):
        return self._experience_cards
    
    @property
    def college_degrees(self):
        return self._college_degrees
   
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
    
    def find_next_border_square(self, current_square_number, atype:str, name:str=None) -> int:
        """Find the next border square of a given type and optional name
            Arguments:
                current_square_number - square number on the game board
                game_board - a GameBoard instance
                atype - the square type to look for. Valid values are 'travel_square', 'corner_square', 'travel_square', and 'occupation_entrance_square'
                name - optional square.name to use for comparison. For example in the UK edition, the travel squares
                       all have different names.
            Returns: the next square number OR None if no square of a given type/name is found.
            BTW, the next_square_number could be < current_square_number if it's past Payday
        """
        squares = []
        next_square_num = None
        if atype=='travel_square':
            squares = self.game_board.travel_squares
        elif atype=='opportunity_square':
            squares=self.game_board.opportunity_squares
        elif atype=='occupation_entrance_square':
            squares = self.game_board.occupation_entrance_squares
        elif atype=='corner_square':
            squares = self.game_board.corner_squares
        
        for square in squares:      # square is a BorderSquare instance, they are in square# order
            if square.square_type == atype and (name is None or square.name==name):
                if square.number > current_square_number:
                    next_square_num = square.number
                    break
        if next_square_num is None:     # wrap-around the board
            next_square_num = squares[0].number
        return next_square_num
    
    def to_JSON(self):
        """Use jsonpickle to serialize the game to JSON as a JSON-compatible dict.
            A CareersGame serialized with jsonpickle can be turned back to python with unpickler.
        """
        return CareersObject.json_pickle(self)
    
if __name__ == '__main__':
    game = CareersGame('Hi-Tech')
    print(game.occupation_list)
    
    
