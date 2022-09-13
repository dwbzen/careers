import uvicorn
from fastapi import FastAPI, Depends
from server.gameManager import CareersGameManager

manager = CareersGameManager()    
app = FastAPI()

@app.get("/", status_code=200)
def get(game: CareersGameManager=Depends(manager)):
    return {}

if __name__ == "__main__":
    uvicorn.run("app:app", port=9000, reload=True)