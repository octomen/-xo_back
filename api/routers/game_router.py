import asyncio
import json
from api.controllers import game_controller
from fastapi import FastAPI
from starlette.websockets import WebSocket

app = FastAPI()


@app.put(path='/game')
def create_game():
    return game_controller.create()


@app.websocket(path='/game/{game_uid}/{user_uid}')
async def game(websocket: WebSocket, game_uid: str, user_uid: str):
    await websocket.accept()
    state = game_controller.join(game_uid, user_uid)
    await websocket.send_text(str(state))
    while True:
        if state.current_user_uid() == user_uid:
            await websocket.send_text(str(game_controller.get_state(game_uid)))
            move = await websocket.receive_text()
            state = game_controller.move(game_uid, user_uid, json.loads(move))
            await websocket.send_text(state)
        else:
            await asyncio.sleep(0.1)


@app.get(path='/game/{game_uid}')
def get_game(game_uid: str):
    return game_controller.get_state(game_uid)
