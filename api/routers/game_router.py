from api.controllers import game_controller
from fastapi import FastAPI

from models.point import Point

app = FastAPI()


@app.get(path='/game/{game_uid}')
def get_game(game_uid: str):
    return game_controller.get_state(game_uid)


@app.post(path='/move/{game_uid}/{user_uid}/{x_coordinate}/{y_coordinate}')
def move(game_uid: str, user_uid: str, x_coordinate: int, y_coordinate: int):
    _ = Point(x_coordinate, y_coordinate)
