from typing import Any, Union
from unicodedata import name
from pydantic import BaseModel, Field
import uvicorn
from fastapi import FastAPI, Depends, status, Form
from datetime import date, datetime
from fastapi.responses import JSONResponse
from careers.server.userManager import CareersUserManager, User
from server.gameManager import CareersGameManager
from game.careersGameEngine import CareersGameEngine

manager = CareersGameManager()    
userManager = CareersUserManager()
app = FastAPI()

@app.get("/", status_code=200)
def get(game: CareersGameEngine=Depends(manager)):
    return {}

@app.get('/user/{userId}')
def getUserById(userId: str):
    return userManager.getUserByUserId(userId)

@app.post('/ready/{userId}/{gameId}/{ready}')
def userReadyToStart(userId: str, gameId: str, ready: bool, gameInstance: CareersGameEngine=Depends(manager)):
    manager.userReady(userId, ready, gameInstance)

@app.put("/user", status_code=200)
def createUser(user: User):
    return userManager.createUser(user)

@app.put('/game/{userId}/{points}', status_code=201)
def createGame(userId: str, points: int):
    """Creates a new game and returns the game id"""
    return manager.create("Hi-Tech", userId, points)

@app.get('/can-start/{gameId}')
def readyToStart(gameInstance: CareersGameManager=Depends(manager)):
    """Determines if the game is ready to start by checking
    the number of players and the ready count"""
    pass

@app.get('/game/details/code/{joinCode}')
def getGameDetails(joinCode: str):
    """
        Before joining a game, the player needs to know the details 
        so they can create the formula
    """
    game = manager.getGameByJoinCode(joinCode)

    if(game is None):
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": "Not Found"})

    return game

@app.get('/game/{gameId}')
def getGame(gameId: str):
    return manager.getGameById(gameId)

@app.get('/game/{gameId}/players')
def getPlayers(gameId: str, gameInstance: CareersGameEngine=Depends(manager)):
    return manager.getPlayers(gameInstance)

@app.post('/game/{gameId}/player/{userId}/{money}/{hearts}/{stars}', status_code=201)
def joinGame(gameId: str, userId: str = None, money: int = 0, hearts: int = 0, stars: int = 0, gameInstance: CareersGameEngine=Depends(manager)):
    user = manager.joinGame(gameId, userId, gameInstance)
    return user

@app.get('/games/{userId}', status_code=200)
def getGames(userId: str):
    """
        Gets all the games the user has created or participates in
    """
    return manager.getGames(userId)

if __name__ == "__main__":
    uvicorn.run("app:app", port=9000, reload=True)