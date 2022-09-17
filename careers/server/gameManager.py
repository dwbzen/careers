"""Not sure what this is going to do yet.
    Probably managed unique GameEngine instances (one per game).
"""

from typing import Any

from careers.game.careersGameEngine import CareersGameEngine

class CareersGameManager(object):

    def __init__(self):
        self.games = {}
        pass

    def create(self):
        pass

    def __call__(self, installationId: str) -> Any:
        """Create a new game engine for the user and return the instance"""
        game = self.games.get(installationId)
    
        if game is None:
            self.games[installationId] = list()

        self.games[installationId].append(CareersGameEngine())
        return self.games[installationId][len(self.games[installationId]) -1]