from typing import Any
from unicodedata import name
from pydantic import BaseModel, Field
import uvicorn
from fastapi import FastAPI, Depends, status, Form
from datetime import date, datetime
from fastapi.responses import JSONResponse
from careers.server.userManager import CareersUserManager, User
from server.gameManager import CareersGameManager
from game.careersGameEngine import CareersGameEngine

gameEngine = CareersGameEngine()
manager = CareersGameManager()    
userManager = CareersUserManager()
app = FastAPI()

@app.get("/", status_code=200)
def get(game: CareersGameManager=Depends(manager)):
    return {}

@app.get('/user/{userId}')
def getUserById(userId: str):
    return userManager.getUserByUserId(userId)

@app.put("/user", status_code=200)
def createUser(user: User):
    return userManager.createUser(user)

@app.put('/game/{userId}/{points}', status_code=201)
def createGame(userId: str, points: int):
    """Creates a new game and returns the game id"""
    return manager.create("Hi-Tech", userId, points)

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

@app.put('/game/start/{gameId}')
def startGame():
    pass

@app.put('/game/{gameId}/player/{userId}/{money}/{hearts}/{stars}', status_code=201)
def joinGame(gameId: str, userId: str, money: int, hearts: int, stars: int, 
        gameInstance: CareersGameEngine=Depends(manager)):
    user = manager.joinGame(gameId, userId)
    return gameInstance.execute_command(f'add player {user["name"]} {user["initials"]} {money} {hearts} {stars}', None)

@app.get('/games/{userId}', status_code=200)
def getGames(userId: str):
    """
        Gets all the games the user has created or participates in
    """
    return manager.getGames(userId)

if __name__ == "__main__":
    uvicorn.run("app:app", port=9000, reload=True)