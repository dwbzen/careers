'''
Created on Aug 26, 2022

@author: don_bacon
'''

import json
from game.borderSquare import BorderSquare, BorderSquareType
from game.gameConstants import GameConstants


class GameBoard(object):
    """Encapsulates a Careers game board border squares.
        This structure does not include the Occupation path squares.
        They are accessed from CareersGame from occupations dictionary.
    """

    def __init__(self, game_layout_filename, game=None):
        """Create a new GameBoard
            Arguments:
                game_layout_filename - the full path to the gameLayout JSON file, for example: "/Compile/careers/resources/gameLayout_Hi-Tech.json"
                game - a CareersGame instance
        """
        self._game_layout_filename = game_layout_filename
        self._occupation_entrance_squares = {}         # dictionary of BorderSquare that are type "occupation_entrance_square" indexed by name
        self._travel_squares = []                      # list of BorderSquare that are type "travel_square"
        self._corner_squares = {}                      # dict of BorderSquare that are type "corner_square" indexed by name
        self._opportunity_squares = []                 # list of BorderSquare that are type 'opportunity_square'
        self._action_squares = {}                      # dict of BorderSquare that are type "action_square" indexed by name
        self._danger_squares = {}                      # dict of BorderSquare that are type "danger_square" indexed by name
        fp = open(game_layout_filename, "r")
        self._game_board_dict = json.loads(fp.read())
        fp.close()
        self._game_layout = self._game_board_dict['layout']
        self._game_layout_dimensions = self._game_board_dict['dimensions']
        self._game_board_size = self._game_layout_dimensions['size']     # the last square number is size-1
        self._types = self._game_board_dict['types_list']        # a list of border square types
        
        self._border_squares = list()
        for border_square_dict in self._game_layout:
            border_square = BorderSquare(border_square_dict, game=game)
            #
            # populate square type lists/dictionaries
            #
            self._border_squares.append(border_square)
            
            if border_square.square_type is BorderSquareType.OCCUPATION_ENTRANCE_SQUARE:
                self._occupation_entrance_squares[border_square.name] = border_square
                
            if border_square.square_type is BorderSquareType.TRAVEL_SQUARE:
                self._travel_squares.append(border_square)
        
            # the corner squares each have their own unique type
            if border_square.square_type in GameConstants.CORNER_SQUARE_TYPES:
                self._corner_squares[border_square.name] = border_square
                
            if border_square.square_type is BorderSquareType.OPPORTUNITY_SQUARE:
                self._opportunity_squares.append(border_square)
            
            if border_square.square_type is BorderSquareType.ACTION_SQUARE:
                self._action_squares[border_square.name] = border_square
            
            if border_square.square_type is BorderSquareType.DANGER_SQUARE:
                self._danger_squares[border_square.name] = border_square
                
            if 'special_processing' in border_square_dict:
                ...    # SpecialProcessing added as part of BorderSquare constructor
    
    @property
    def border_squares(self) ->list:    # list of BorderSquare
        return self._border_squares
    
    def get_square(self, num) -> BorderSquare:
        return self._border_squares[num]
    
    @property
    def game_layout(self) ->list:       # list of dict
        return self._game_layout
    
    @property
    def game_layout_dimensions(self) ->dict:
        return self._game_layout_dimensions

    @property
    def game_board_size(self):
        return self._game_board_size
    
    @property
    def occupation_entrance_squares(self) ->dict:
        return self._occupation_entrance_squares
    
    @property
    def travel_squares(self) ->list:
        return self._travel_squares
    
    @property
    def corner_squares(self) ->dict:
        return self._corner_squares
    
    @property
    def opportunity_squares(self):
        return self._opportunity_squares
    
    @property
    def action_squares(self):
        return self._action_squares
    
    @property
    def danger_squares(self):
        return self._danger_squares
    
    @property
    def types(self) ->list:
        return self._types
    
    