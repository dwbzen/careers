"""Not sure what this is going to do yet.
    Probably managed unique GameEngine instances (one per game).
"""

from array import array
from multiprocessing.dummy import Array
from fastapi.encoders import jsonable_encoder
from typing import Any, List, Optional
import uuid
import json
from datetime import date, datetime

import dotenv
from pydantic import BaseModel, Field
from pymongo import MongoClient
import pymongo
from game.careersGameEngine import CareersGameEngine

class CareersGameManager(object):

    def __init__(self):
        self.games = {}
        self.config = dotenv.dotenv_values(".env")
        self.mongo_client = MongoClient(self.config["DB_URL"])
        self.database = self.mongo_client["careers"]
        self.database["games"].create_index('players')

    def create(self, edition: str, installationId: str, points: int):
        """
            Creates a new game instance. Stores it in memory for quick retreival
            but also stores it in mongo for later lookups
        """
        gameEngine = CareersGameEngine()
        gameId = json.loads(gameEngine.create(edition, installationId, 'points', points).message)['gameId']
        game = Game(_id=gameId, createdBy=installationId, points=points, players=[installationId], createdDate=datetime.now())

        self.database["games"].insert_one(jsonable_encoder(game))
        self.games[gameId] = gameEngine

        return gameId

    def getGames(self, installationId: str) -> Any:
        """
            Gets all of the games this user participates in
        """
        return list(self.database["games"].find({"players": installationId}))

    def __call__(self, gameId: str = None) -> CareersGameEngine:
        """Create a new game engine for the user and return the instance"""
        if(gameId is None):
            return None

        if(gameId in self.games):
            return self.games[gameId]
        else: 
            dbGame = self.database["games"].find_one({"_id": gameId})
            # Create a new GameEngine from this game id
            self.games[gameId] = CareersGameEngine()
            self.games[gameId].load(gameId)
            return self.games[gameId]

class Game(BaseModel):
    id: str = Field(alias="_id")
    createdBy: str = Field(...)
    createdDate: datetime = Field(...)
    points: int = Field(...)
    edition: str = Field(default="Hi-Tech")
    players: List[str] = Field()