'''
Created on Aug 6, 2022

@author: don_bacon
'''

from game.environment import Environment
from game.player import Player
import json, random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Union

from game.opportunityCardDeck import OpportunityCardDeck
from game.experienceCardDeck import ExperienceCardDeck
from game.gameState import GameState
from game.occupation import Occupation
from game.gameBoard import GameBoard
from game.borderSquare import BorderSquare, BorderSquareType
from game.occupationSquare import OccupationSquare
from game.gameSquare import GameSquare
from game.careersObject import CareersObject
from threading import Lock
from game.boardLocation import BoardLocation
from game.gameParameters import GameParameters
from game.gameConstants import GameConstants, GameParametersType, GameType
from game.turnHistory import TurnHistory, Turn

class CareersGame(CareersObject):
    """
    Represents a Careers Game instance.
        The CareersGame model class has instances of all the components used in game play:
        Opportunity and Experience card decks, the game board, parameters for a given edition, occupations, players, and the game state.
        
    """
    _lock = Lock()
    
    def __init__(self, edition_name:str,  installationId:str, total_points:int, game_id:str, game_type="points", game_parameters_type="prod"):
        """CareersGame Constructor
            Arguments:
                installationId - An ID that uniquely identifies the game's creator - a.k.a the game master
                edition_name - the name of the edition to create. This must be a key in editions.json file.
                total_points - total number of points in the success formula or in a timed game, the number of minutes.
                game_id - a Globally Unique Identifier for this game (guid). If not provided, one is generated from the current date/time.
            Raises:
                ValueError if there is no such edition
            Saved games are indexed by installationId. This is the primary search key used to search for saved games.
            It's the responsibility of the front end GUI to provide this.
        """
        self._installationId = installationId
        self._edition_name = edition_name
        self._game_parameters_type = GameParametersType[game_parameters_type.upper()]      # can be "test" or "prod"
        self._env = Environment.get_environment()
        self._resource_folder = self._env.get_resource_folder()     # base resource folder
        self._game_parameters_filename = None
        self._occupations_filename = None
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
        self._game_type = GameType[game_type.upper()]  # 'points', 'timed' (which is not yet supported), or 'solo'

        #
        # if a gameId is not provided, create one
        #
        if game_id is None or game_id.lower()=="none":
            # create a unique ID for this game, used for logging    
            self._gameId = self._create_game_id()
        else:
            self._gameId = game_id
            
        #
        # create & initialize the GameState which includes a list of Players
        #
        self._game_state = GameState(self._gameId, total_points, self._game_type, self._game_parameters_type)

        self._game_constants = GameConstants({'edition':edition_name})
        self._solo = None     # True if number of players == 1, set when adding players
        self._start_datetime:datetime = None
        self._end_datetime:datetime = None

        
    def _load_game_configuration(self):
        """Loads the game parameters and occupations JSON files for this edition.
        
        """
        game_params_type = self._game_parameters_type.value
        self._game_parameters_filename = f'{self._resource_folder}/{self._edition_name}/gameParameters_{game_params_type}.json'
            
        with open(self._game_parameters_filename, "r") as fp:
            jtxt = fp.read()
            self._game_parameters = GameParameters(json.loads(jtxt))

        self._occupations_filename = f'{self._resource_folder}/{self._edition_name}/occupations.json'
        with open(self._occupations_filename, "r") as fp:
            jtxt = fp.read()
            occupations_dict = json.loads(jtxt)
            self._occupation_names = occupations_dict['occupations']
        
        # load the individual occupation files
        self._occupations = self.load_occupations()     # dictionary of Occupation instances keyed by name
        
        self._turn_outcome_parameters_filename = f'{self._resource_folder}/{self._edition_name}/turnOutcomeParameters.json'
        with open(self._turn_outcome_parameters_filename, "r") as fp:
            jtxt = fp.read()
            turn_outcome_dict = json.loads(jtxt)
            self._turn_outcome_parameters = turn_outcome_dict['turn_outcome_parameters']
   

    def _create_game_id(self) ->str :
        """Create a unique game id (guid) for this game.
            This method acquires a lock to insure uniqueness in a multi-process/web environment.
            Format is based on current date and time and installationId for example ZenAlien2013_20220908-140952-973406-27191
        """
        CareersGame._lock.acquire()
        today = datetime.now()
        gid = self.installationId +  '_{0:d}{1:02d}{2:02d}_{3:02d}{4:02d}{5:02d}_{6:06d}_{7:05d}'\
            .format(today.year, today.month, today.day, today.hour, today.minute, today.second, today.microsecond, random.randint(10000,99999))
        CareersGame._lock.release()
        return gid
    
    def _create_opportunity_deck(self):
        self._opportunities = OpportunityCardDeck(self._resource_folder, self._edition_name)
    
    def _create_experience_deck(self):
        self._experience_cards = ExperienceCardDeck(self._resource_folder, self._edition_name)
        
    def _create_game_board(self) -> GameBoard:
        game_layout_filename = f'{self._resource_folder}/{self._edition_name}/gameLayout.json'
        game_board = GameBoard(game_layout_filename, game=self)
        return game_board

    def load_occupations(self) -> Dict[str, Occupation]:
        """Loads individual occupation JSON files for this edition.
            Arguments: occupation_list - a list of occupation names
            Returns: a dict with the occupation name as the key and contents
                of the corresponding occupation JSON file (as a dict) as the value.
                If the occupation JSON file doesn't exist, the value is None.
            Note: the filename is the occupation name + "_" + the edition_name + ".json"
                The file path is the resource_folder set in the Environment
        """
        occupations:Dict[str, Occupation] = {}
        for name in self._occupation_names:
            filepath = f'{self._resource_folder}/{self._edition_name}/{name}.json'
            p = Path(filepath)
            if p.exists():
                fp = open(filepath, "r")
                occupation_dict = json.loads(fp.read())
                # create an Occupation object for this occupation
                occupation = Occupation(occupation_dict, game=self)
                occupations[name] = occupation
            else:
                occupations[name] = None
        return occupations

    
    def _load_college_degrees(self) -> Dict[str, Union[List[int] ,List[str], int]]:
        fp = open(f'{self._resource_folder}/{self._edition_name}/collegeDegrees.json', "r")
        degrees = json.loads(fp.read())
        return degrees
    
    @property
    def edition(self):
        return self._edition
    
    @property
    def edition_name(self):
        return self._edition_name
    
    @property
    def solo(self) -> bool | None:
        return self._solo
    
    @solo.setter
    def solo(self, value:bool):
        self._solo = value
    
    @property
    def game_board(self) -> GameBoard:
        return self._game_board
    
    def get_occupation(self, name) -> Occupation:
        return self.occupations.get(name, None)
        
    def get_border_square(self, num:int) -> BorderSquare:
        """Convenience method to get a BorderSquare instance from the GameBoard
        """
        return self._game_board.get_square(num)
    
    def get_occupation_square(self, name:str, num:int) -> OccupationSquare | None:
        occupation = self.occupations.get(name, None)
        gameSquare = occupation.occupationSquares[num] if occupation is not None else None
        return gameSquare
    
    def get_game_square(self, board_location:BoardLocation) ->GameSquare:
        """Gets the GameSquare instance for a given BoardLocation
            Returns: a GameSquare instance - BorderSquare or OccupationSquare depending on the BoardLocation
        """
        game_square = None
        if board_location.occupation_name is not None and board_location.occupation_square_number >= 0:     # location is an OccupationSquare
            game_square = self.get_occupation_square(board_location.occupation_name, board_location.occupation_square_number)
        else:
            game_square = self.get_border_square(board_location.border_square_number)
        return game_square
        
    
    def get_game_layout_dimensions(self) -> dict:
        """size: (number of squares), sides: (4-element list of #squares/side)
        """
        return self.game_board.game_layout_dimensions
    

    def get_game_board_size(self) -> int:
        return self.game_board.game_board_size
    
    
    @property
    def game_parameters(self) -> GameParameters:
        return self._game_parameters
    
    @property
    def game_state(self):
        return self._game_state
    
    @property
    def gameId(self):
        return self._gameId
    
    @property
    def installationId(self):
        return self._installationId
    
    @installationId.setter
    def installationId(self, value):
        self._installationId = value
    
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
    
    @property
    def game_constants(self) -> GameConstants:
        return self._game_constants
   
    @property
    def game_parameters_type(self) -> GameParametersType:
        return self._game_parameters_type
    
    @property
    def turn_outcome_parameters(self) -> dict:
        return self._turn_outcome_parameters
    
    def add_player(self, aplayer:Player):
        """Adds a new Player to the game.
            This also creates a TurnHistory for the Player, and adds an initial Turn object and before player_info
        """
        self.game_state.add_player(aplayer)
        #
        # create a TurnHistory
        #
        turn_history = TurnHistory(aplayer.number, self._turn_outcome_parameters)
        turn_number = 0
        turn = Turn(aplayer.number, turn_number)
        turn_history.add_turn(turn)
        turn_history.add_player_info(turn_number, TurnHistory.BEFORE_KEY, aplayer.player_info(include_successFormula=True, outputFormat="dict" ))
        aplayer.turn_history = turn_history
        self._solo = self.game_state.number_of_players == 1
    
    def complete_player_move(self) -> Player | None:
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
            
    def is_game_complete(self) -> bool:
        """Iterates over the players to see who, if anyone, has won.
            Returns: True if there's a winner, else False.
                    sets self.winning_player to the Player who won.
            NOTE - returns the first winning player if there happens to be more than 1.
            To prevent this from happening, this should be called at the end of each player's turn.
        """
        return self.game_state.is_game_complete()
    
    def start_game(self):
        """
        Initializes game state and starts the game
        """
        pass
        
    def end_game(self)->int:
        self.game_duration = self.game_state.get_elapsed_time()
        return self.game_duration
    
    def find_next_border_square(self, current_square_number, atype:BorderSquareType, name:str=None) -> Tuple[int,BorderSquare]:
        """Find the next border square of a given type and optional name
            Arguments:
                current_square_number - square number on the game board
                game_board - a GameBoard instance
                atype - the square type to look for. Valid values are 'travel_square', 'corner_square', 'travel_square', and 'occupation_entrance_square'
                name - optional square.name to use for comparison. For example in the UK edition, the travel squares
                       all have different names.
            Returns: a 2-item tupple : the next square number OR None if no square of a given type/name is found,
                     and the game_square instance.
            BTW, the next_square_number could be < current_square_number if it's past Payday
        """
        squares = []
        next_square_num = None
        game_square = None
        if atype is BorderSquareType.TRAVEL_SQUARE:
            squares = self.game_board.travel_squares
            
        elif atype is BorderSquareType.OPPORTUNITY_SQUARE:
            squares=self.game_board.opportunity_squares
            
        elif atype is BorderSquareType.OCCUPATION_ENTRANCE_SQUARE:
            squares = self.game_board.occupation_entrance_squares
            
        elif atype is BorderSquareType.CORNER_SQUARE:
            squares = self.game_board.corner_squares
        
        for square in squares:      # square is a BorderSquare instance, they are in square# order
            if square.square_type is atype and (name is None or square.name==name):
                if square.number > current_square_number:
                    next_square_num = square.number
                    game_square = square
                    break
        if next_square_num is None:     # wrap-around the board
            square = squares[0]
            next_square_num = square.number
            game_square = square
            
        return next_square_num, game_square
    
    def find_border_square(self, name:str, starting_square_number:int=0) -> BorderSquare | None:
        """Find the BorderSquare with the name provided.
            Argument:
                name - the name of the BorderSquare to find. NOT case sensitive.
                starting_square_number - the square number to start the search. Default is 0.
                
            Returns:
                BorderSquare instance or None if not found.
        """
        bs = None
        indicies = [(i+starting_square_number)%42 for i in range(42)]
        
        for i in indicies:
            square = self.game_board.border_squares[i]
            if square.name.lower() == name.lower():
                bs = square
                break
        return bs
    
    def to_JSON(self) -> str:
        """Use jsonpickle to serialize the game to JSON as a JSON-compatible dict.
            A CareersGame serialized with jsonpickle can be turned back to python with unpickler.
        """
        return CareersObject.json_pickle(self)
    
    def _load(self, game_dict:dict):
        """Loads a previously saved game.
            Assumes the values for the following already set (when this instance was created):
            edition_name, installationId, total_points, game_id, game_type, game_parameters_type
        """
        game_state_dict = game_dict["gameState"]
        #self.game_state.number_of_players = game_state_dict["number_of_players"]
        self.game_state.current_player_number = game_state_dict["current_player_number"]
        self.game_state.turns = game_state_dict["turns"]
        self.game_state.turn_number = game_state_dict["turn_number"]
        self.game_state.total_points = game_state_dict["total_points"]
        self.game_state.game_complete = game_state_dict["game_complete"]
        self.game_state.restored = True
        
        # load players and other game info
        self.game_state._load(game_state_dict)
        
        #load Opportunity and Experience card decks
        opportunity_deck = game_dict["opportunity_deck"]
        experience_deck = game_dict["experience_deck"]
        self.opportunities.next_index = opportunity_deck["next_index"]
        self.opportunities.cards_index = opportunity_deck["cards_index"]
        self.experience_cards.next_index = experience_deck["next_index"]
        self.experience_cards.cards_index = experience_deck["cards_index"]
        
        # load player Opportunity and Experience cards
        players = game_state_dict["players"]
        for player_dict in players:
            initials = player_dict["initials"]
            player:Player = self.game_state.get_player_by_initials(initials)
            if player.number == self.game_state.current_player_number:
                self.game_state.current_player = player
            opportunity_cards = player_dict["opportunity_cards"]    # List[str], format "<Opportunity card_number>:<card_text>"
            experience_cards = player_dict["experience_cards"]      # List[str], format "<Experience card_number>:card_type or text <n> spaces"
            
            for card in opportunity_cards:
                clist = card.split(":")
                card_number = int(clist[0])
                thecard = self.opportunities.deck[card_number]
                player.add_opportunity_card(thecard)
            
            for card in experience_cards:
                clist = card.split(":")
                card_number = int(clist[0])
                thecard = self.experience_cards.deck[card_number]
                player.add_experience_card(thecard)
            
            print(f'{player.player_initials} loaded')
        
if __name__ == '__main__':
    print(CareersGame.__doc__)
    

def restore_game(game_id:str, game_text:str=None) -> CareersGame|None:
    print(f'restoring game "{game_id}"')
    game_dict = None
    if game_text is None:
        env = Environment.get_environment()
        games_folder = env.games_base
        gamefile = f'{games_folder}/{game_id}_game.json'
        with open(gamefile, "r") as fp:
            game_dict = json.load(fp)
    else:
        game_dict = json.loads(game_text)
    game_state_dict = game_dict["gameState"]
    
    total_points = game_state_dict["total_points"]
    game_type = game_state_dict["game_type"]
    game_parameters_type = game_state_dict["game_parameters_type"]
    
    edition_name =  game_dict["edition_name"]
    installationId =  game_dict["installationId"]
    #  edition_name:str,  installationId:str, total_points:int, game_id:str, game_type="points", game_parameters_type="prod"):
    careers_game = CareersGame(edition_name, installationId, total_points, game_id, game_type, game_parameters_type)
    careers_game._load(game_dict)
    
    return careers_game
