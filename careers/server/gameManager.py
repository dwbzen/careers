"""Not sure what this is going to do yet.
    Probably managed unique GameEngine instances (one per game).
"""

from array import array
import imp
from multiprocessing.dummy import Array
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from typing import Any, List, Optional
import uuid
import json
import random
import string
from datetime import date, datetime
from uuid import uuid4

import dotenv
from pydantic import BaseModel, Field
from pymongo import MongoClient
import pymongo
from careers.server.userManager import CareersUserManager, User
from game.careersGame import CareersGame
from game.careersGameEngine import CareersGameEngine
from game.gameParameters import GameParameters
from game.player import Player

class Game(BaseModel):
    id: str = Field(alias="_id", default=None)
    createdBy: str = Field(...)
    createdDate: datetime = Field(...)
    edition: str = Field(default="Hi-Tech")
    joinCode: str = Field(...)
    gameParameters: Any = Field(...)
    gameState: Any = Field(...)

class CareersGameManager(object):

    def __init__(self):
        self.games = {}
        self.config = dotenv.dotenv_values(".env")
        self.mongo_client = MongoClient(self.config["DB_URL"])
        self.database = self.mongo_client["careers"]
        self.database["games"].create_index('players')
        self.userManager = CareersUserManager()

    def create(self, edition: str, userId: str, points: int):
        """
            Creates a new game instance. Stores it in memory for quick retreival
            but also stores it in mongo for later lookups
        """
        gameEngine = CareersGameEngine()
        gameId = json.loads(gameEngine.create(edition, userId, 'points', points).message)['gameId']

        "Add the creator as a player"
        user = self.userManager.getUserByUserId(userId)
        gameEngine.execute_command(f'add player {user["name"]} {user["initials"]} {userId} {user["email"]}', None)

        game = Game(_id=gameId, 
            createdBy=userId, 
            createdDate=datetime.now(), 
            joinCode=''.join(random.choices(string.ascii_letters, k=5)),
            gameParameters = gameEngine.careersGame.game_parameters._game_parameters,
            gameState= json.loads(gameEngine.careersGame.game_state.to_JSON()))

        self.database["games"].insert_one(jsonable_encoder(game))
        self.games[gameId] = gameEngine

        return game

    def getGameByJoinCode(self, joinCode: str):
        """
            Returns a game by join code
        """
        return self.database["games"].find_one({"joinCode": joinCode})

    def getGames(self, installationId: str) -> Any:
        """
            Gets all of the games this user participates in
        """
        return list(self.database["games"].find({"players": installationId}))

    def joinGame(self, gameId: str, userId: str) -> User:
        self.database["games"].update_one({"_id": gameId}, {'$push': {'players': userId}})
        return self.userManager.getUserByUserId(userId)

    def __call__(self, gameId: str = None) -> CareersGameEngine:
        """Create a new game engine for the user and return the instance"""
        if(gameId is None):
            return None

        if(gameId in self.games):
            return self.games[gameId]
        else: 
            # Create a new GameEngine from this game id
            self.games[gameId] = CareersGameEngine()
            self.games[gameId].load(gameId)
            return self.games[gameId]
