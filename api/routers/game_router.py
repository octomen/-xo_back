from api.controllers import game_controller
from fastapi import FastAPI, WebSocket

app = FastAPI()


@app.put(path='/game')
def create_game():
    return game_controller.create()


@app.websocket(path='/game/{game_uid}/{user_uid}')
async def game(websocket: WebSocket, game_uid: str, user_uid: str):
    await websocket.accept()
    state = game_controller.join(game_uid, user_uid)
    await websocket.send_message(state)
    while True:
        move = await state[game_controller.get_current_sign(state)].recieve_message()
        game_controller.move(game_uid, None, move)
        await websocket.send_message(game_controller.get_state(game_uid))


@app.get(path='/game/{game_uid}')
def get_game(game_uid: str):
    return game_controller.get_state(game_uid)
