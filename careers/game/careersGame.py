'''
Created on Aug 6, 2022

@author: don_bacon
'''

from careers.environment import Environment
from game.player import Player
import json
from pathlib import Path
from game.opportunityCardDeck import OpportunityCardDeck
from game.experienceCardDeck import ExperienceCardDeck
from game.borderSquare import BorderSquare
from game.occupationSquare import OccupationSquare
from game.gameState import GameState

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
        #
        # load the game board
        #
        self._game_board = self._create_game_board()   # list of BorderSquare
        #
        # create & initialize the game state
        #
        self._game_state = GameState(total_points)
        
    def _load_game_configuration(self):
        """Loads the game parameters and occupations JSON files for this edition.
        
        """
        fp = open(self._resource_folder + "/gameParameters_" + self._edition_name + ".json", "r")
        jtxt = fp.read()
        self._game_parameters = json.loads(jtxt)
        fp.close()

        fp = open(self._resource_folder + "/occupations_" + self._edition_name + ".json", "r")
        jtxt = fp.read()
        occupations = json.loads(jtxt)
        self._occupation_list = occupations['occupations']
        fp.close()
        
        # load the individual occupation files
        self._occupations = self.load_occupations()
        # create the layout (occupation squares) for each occupation
        self._occupation_squares_dict = self._create_occupation_squares()
        
    def _create_opportunity_deck(self):
        self._opportunities = OpportunityCardDeck(self._resource_folder, self._edition_name)
    
    def _create_experience_deck(self):
        self._experience_cards = ExperienceCardDeck(self._resource_folder, self._edition_name)
        
    def _create_game_board(self):
        fp = open(self._resource_folder + "/gameLayout_" + self._edition_name + ".json", "r")
        self._game_board_dict = json.loads(fp.read())
        self._game_layout = self._game_board_dict['layout']
        game_board = list()
        for border_square_text in self._game_layout:
            border_square = BorderSquare(border_square_text)
            game_board.append(border_square)
        return game_board

    def load_occupations(self) -> dict:
        """Loads individual occupation JSON files for this edition.
            Arguments: occupation_list - a list of occupation names
            Returns: a dict with the occupation name as the key and contents
                of the corresponding occupation JSON file as the value.
                If the occupation JSON file doesn't exist, the value is None.
        """
        occupations = dict()
        for name in self._occupation_list:
            filepath = self._resource_folder + "/" + name + "_" + self._edition_name + ".json"
            p = Path(filepath)
            if p.exists():
                fp = open(filepath, "r")
                occupation = json.loads(fp.read())
                occupations[name] = occupation
            else:
                occupations[name] = None
        return occupations
    
    def _create_occupation_squares(self) -> dict:
        """For each Occupation create a list of OccupationSquare corresponding to the "occupationSquares" of that occupation.
            Returns: a dictionary with the occupation name as the key, and a [OccupationSquare] as the value.
        """
        occupation_squares_dict = dict()
        for occupation_name in self.occupation_list:
            squares = self.occupations[occupation_name]['occupationSquares']
            occupation_squares = list()
            for occupation_square_dict in squares:
                occupation_square = OccupationSquare(occupation_square_dict)
                occupation_squares.append(occupation_square)
            occupation_squares_dict[occupation_name] = occupation_squares
        return occupation_squares_dict
    
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
    def game_state(self):
        return self._game_state
    
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
    
    def add_player(self, aplayer):
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
    
    
