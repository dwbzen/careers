import uvicorn
from fastapi import FastAPI, Depends

from careers.server.gameManager import CareersGameManager
from careers.game.careersGameEngine import CareersGameEngine

gameEngine = CareersGameEngine()
manager = CareersGameManager()    
app = FastAPI()

@app.get("/", status_code=200)
def get(game: CareersGameManager=Depends(manager)):
    return {}

@app.post('/game/{installationId}/{points}', status_code=201)
def createGame(installationId: str, points: int, gameInstance: CareersGameEngine=Depends(manager)):
    """Creates a new game and returns the game id"""
    return gameInstance.create("Hi-Tech", 'points', installationId, points)

if __name__ == "__main__":
    uvicorn.run("app:app", port=9000, reload=True)