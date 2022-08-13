'''
Created on Aug 12, 2022

@author: don_bacon
'''

from game import CareersGame, SuccessFormula, Player

class GameRunner(object):
    """A command-line text version of Careers game play used for testing.
        Uses a default game of 100 points and 2 players.
    """

    def __init__(self, total_points, players:list(Player)):
        """
        Constructor
        """
        self.game = CareersGame('Hi-Tech', total_points)
        self.total_points = total_points
        #
        # initialize the players
        #
        for player in players:
            player.cash = self.game.game_parameters['starting_cash']
            player.salary = self.game.game_parameters['starting_salary']
            self.game.add_player(player)
            
        self._trace = False     # traces the action by describing each step
            
    
    def run_game(self):
        pass
        
        
if __name__ == '__main__':

    total_points = 100
    players = []
    player1 = Player(0, name='Don', initials='DWB')
    sf = SuccessFormula(stars=40, hearts=10, cash=50)
    player1.success_formula = sf
    players.append(player1)
    
    player2 = Player(1, name="Scott", initials="SFP")
    sf = SuccessFormula(stars=20, hearts=40, cash=40)
    player2.success_formula = sf
    players.append(player2)

    game_runner = GameRunner(total_points, players)
    game_runner.run_game()
    
    
