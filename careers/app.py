import uvicorn
from fastapi import FastAPI, Depends, status

from fastapi.responses import JSONResponse
from server.gameManager import CareersGameManager
from game.careersGameEngine import CareersGameEngine

gameEngine = CareersGameEngine()
manager = CareersGameManager()    
app = FastAPI()

@app.get("/", status_code=200)
def get(game: CareersGameManager=Depends(manager)):
    return {}

@app.post('/game/{installationId}/{points}', status_code=201)
def createGame(installationId: str, points: int):
    """Creates a new game and returns the game id"""
    return manager.create("Hi-Tech", installationId, points)

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

@app.put('/game/{gameId}/player/{playerName}/{playerInitials}/{money}/{hearts}/{stars}', status_code=201)
def joinGame(gameId: str, playerName: str, playerInitials: str, money: int, hearts: int, stars: int, 
        gameInstance: CareersGameEngine=Depends(manager)):
    manager.joinGame(gameId, playerName, playerInitials)
    return gameInstance.execute_command(f'add player {playerName} {playerInitials} {money} {hearts} {stars}', None)

@app.get('/games/{installationId}', status_code=200)
def getGames(installationId: str):
    """
        Gets all the games the user (installationId) has created or participates in
    """
    return manager.getGames(installationId)

if __name__ == "__main__":
    uvicorn.run("app:app", port=9000, reload=True)