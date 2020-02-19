from api.controllers import game_controller
from fastapi import FastAPI

app = FastAPI()


@app.get(path='/game/{game_uid}')
def get_game(game_uid: str):
    return game_controller.get_state(game_uid)
