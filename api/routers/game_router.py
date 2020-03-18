from fastapi import FastAPI
from starlette.websockets import WebSocket
from api.modules.socket import WebSocketProxy
from api.controllers import game, user

app = FastAPI()


@app.websocket(path='/game/{game_uid}/{user_uid}')
async def connect_as_gamer(websocket: WebSocket, game_uid: str, user_uid: str):
    await websocket.accept()
    ws_proxy = WebSocketProxy(websocket)
    game_ctl = game.get_or_create(game_uid)
    user_ctl = user.User(ws_proxy, user_uid)
    game_ctl.add_gamer(user_ctl)
    await user_ctl.start_serve()
