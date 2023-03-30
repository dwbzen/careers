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
from game.careersGame import CareersGame, restore_game
from game.careersGameEngine import CareersGameEngine
from game.gameParameters import GameParameters
from game.player import Player

class Game(BaseModel):
    id: str = Field(alias="_id", default=None)
    gameId: str = Field(alias="game_id", default=None)
    createdBy: str = Field(alias="installationId", default=None)
    createdDate: datetime = Field(...)
    edition: str = Field(alias="edition_name", default="Hi-Tech")
    joinCode: str = Field(alias="join_code", default=None)
    gameState: Any = Field(default=None)
    opportunityDeck: Any = Field(alias="opportunity_deck", default=None)
    experienceDeck: Any = Field(alias="experience_deck", default=None)
    players: Any = Field(default=None)

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
        newGame = gameEngine.create(edition, userId, 'points', points).message
        gameId = json.loads(newGame)['gameId']

        "Add the creator as a player"
        user = self.userManager.getUserByUserId(userId)
        gameEngine.execute_command(f'add player {user["name"]} {user["initials"]} {userId} {user["email"]} 0 0 0', None)

        gameDict = self.getGameDictionary(gameId, userId, "Hi-Tech", gameEngine.careersGame)

        game = Game(_id=gameId, 
            createdDate=datetime.now(), 
            gameState = gameDict["gameState"],
            players=[userId])

        game.joinCode = ''.join(random.choices(string.ascii_letters, k=5))
        game.gameId = gameId
        game.createdBy = userId
        game.experienceDeck = gameDict["experience_deck"]
        game.opportunityDeck = gameDict["opportunity_deck"]

        self.database["games"].insert_one(jsonable_encoder(game))
        self.games[gameId] = gameEngine

        return game

    def getGameDictionary(self, gameId: str, userId: str, edition: str, gameInstance: CareersGame)  -> dict[str, any]:
        """Create a savable dictionary from the game (copied from careersengine.save())"""
        game_dict = {"game_id":gameId, "installationId": userId, "edition_name":edition}
        game_dict["gameState"] = gameInstance.game_state.to_dict()
        
        opportunity_deck = {"next_index":gameInstance.opportunities.next_index, "cards_index":gameInstance.opportunities.cards_index}
        experience_deck = {"next_index":gameInstance.experience_cards.next_index, "cards_index":gameInstance.experience_cards.cards_index}
        game_dict["opportunity_deck"] = opportunity_deck
        game_dict["experience_deck"] = experience_deck
        
        return game_dict

    def getPlayers(self, gameEngine: CareersGameEngine):
        """Get all the players"""
        #return json.loads(gameEngine.game_state.to_JSON())    
        game = self.getGameById(gameEngine.gameId)
        return game
    
    def userReady(self, userId: str, ready: bool, gameEngine: CareersGameEngine):
        """Mark a user ready to start. All users must mark ready before game can begin"""

        if(ready == True):
            self.database['games'].update_one({"_id": gameEngine.gameId}, {'$addToSet': {'ready': userId}}, upsert=True)
        else:
            self.database['games'].update_one({"_id": gameEngine.gameId}, {'$pull': {'ready': userId}})

    def getGameByJoinCode(self, joinCode: str):
        """
            Returns a game by join code
        """
        return self.database["games"].find_one({"joinCode": joinCode})

    def getGameById(self, gameId: str) -> Game:
        """Gets a game details by id"""
        return self.database["games"].find_one({"_id": gameId})

    def getGames(self, installationId: str) -> Any:         
        """
            Gets all of the games this user participates in
        """
        return list(self.database["games"].find({"players": installationId}))
    
    def updatePlayerFormula(self, userId: str, hearts:int, stars: int, money: int, gameEngine: CareersGameEngine):
        """Updates the specified users formula"""
        user = gameEngine.get_player(userId)

        gameEngine.execute_command(f"update {userId} {hearts} {stars} {money}", user)
        self.saveGame(gameEngine.gameId, userId, gameEngine)

    def joinGame(self, gameId: str, userId: str, gameEngine: CareersGameEngine) -> User:
        """Joins a game and updates a users number in the db"""
        self.database["games"].update_one({"_id": gameId}, {'$push': {'players': userId}})
        user = self.userManager.getUserByUserId(userId)

        """The player will join with an empty formula"""
        updatedUser = json.loads(gameEngine.execute_command(f'add player {user["name"]} {user["initials"]} {userId} {user["email"]} 0 0 0', None).json_message)
        user['number'] = updatedUser['userMessage']['number']

        self.userManager.updateUser(user)
        self.saveGame(gameId, userId, gameEngine)
        return user

    def saveGame(self, gameId: str, userId: str, gameEngine: CareersGameEngine) -> None:
        """Save the state of the game"""

        game = self.getGameDictionary(gameId, userId, "Hi-Tech", gameEngine.careersGame)

        self.database['games'].update_one({"_id": gameEngine.gameId}, 
            {"$set": 
                {
                    'gameState': game["gameState"],
                    'opportunity_deck': game["opportunity_deck"],
                    'experience_deck': game['experience_deck']
                }
            })

    def __call__(self, gameId: str = None) -> CareersGameEngine:
        """Create a new game engine for the user and return the instance"""
        if(gameId is None):
            return None

        if(gameId in self.games):
            return self.games[gameId]
        else: 
            dbGame = self.getGameById(gameId)
            game = restore_game(gameId, json.dumps(dbGame))

            # Create a new GameEngine from this game id
            engine = CareersGameEngine(game, gameId)
            engine.game_state = game.game_state
            self.games[gameId] = engine

            #self.games[gameId].execute_command(f"load {gameId}", None)
            return self.games[gameId]