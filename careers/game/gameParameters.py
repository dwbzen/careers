'''
Created on Oct 19, 2022

@author: dwbze
'''

    

class GameParameters(object):
    '''
    Encapsulates global game parameters for this game edition.
    '''


    def __init__(self, params:dict):
        self._game_parameters = params
        self._starting_salary = params.get("starting_salary", 2000)
        self._starting_cash = params.get("starting_cash", 2000)
        self._currency = params.get("currency","dollars")
        self._currency_symbol = params.get("currency_symbol", u'$')
        self._date_format = params.get("date_format", "yyyy-mm-dd")
        self._starting_experience_cards = params.get("starting_experience_cards", 0)
        self._starting_opportunity_cards = params.get("starting_opportunity_cards", 0)
        self._default_game_points = params.get("default_game_points", 100)
        self._default_game_minutes = params.get("default_game_minutes", 60)
        self._allow_negative_experience = (params.get("allow_negative_experience", 0) == 1)
    
    def game_parameters(self):
        return self._game_parameters
    
    def get_param(self, param_name):
        return self._game_parameters.get(param_name, None)
    