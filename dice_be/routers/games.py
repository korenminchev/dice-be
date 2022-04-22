from fastapi import APIRouter, WebSocket, Header
from odmantic import ObjectId
from starlette.websockets import WebSocketDisconnect

from .users import get_user_by_id
from ..dependencies import playground
from ..exceptions import GameNotFound
from ..managers.games import GameManager
from ..models.games import Code, GameData
from ..models.users import User

router = APIRouter(
    prefix='/games',
    tags=["Games"],
)


@router.post('/', response_model=Code)
async def create_game():
    return playground.create_game()


@router.get('/{code}/', response_model=GameData, responses=GameNotFound.response())
async def get_game(code: str):
    return playground.get_game(code).game_data


@router.websocket("/{code}/ws")
async def websocket_endpoint(code: Code, websocket: WebSocket, id: ObjectId = Header(...)):
    user: User = await get_user_by_id(id)
    game: GameManager = playground.get_game(code)

    await websocket.accept()
    await game.add_player(user, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await game.handle_json(user, data)
    except WebSocketDisconnect:
        await game.handle_disconnect(user)
