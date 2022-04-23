"""
Handle all game related API
"""

from fastapi import APIRouter, WebSocket, Header
from odmantic import ObjectId
from starlette.websockets import WebSocketDisconnect

from dice_be.routers.users import get_user_by_id
from dice_be.dependencies import playground
from dice_be.exceptions import GameNotFound
from dice_be.managers.games import GameManager
from dice_be.models.games import Code, GameData
from dice_be.models.users import User

router = APIRouter(
    prefix='/games',
    tags=["Games"],
)


@router.post('/', response_model=Code)
async def create_game():
    """
    Creates a new game
    """
    return playground.create_game()


@router.get('/{code}/', response_model=GameData, responses=GameNotFound.response())
async def get_game(code: str):
    """
    Get info about the game, use this before attempting to join
    """
    return playground.get_game(code).game_data


# pylint:disable=redefined-builtin, invalid-name
@router.websocket("/{code}/ws/")
async def websocket_endpoint(code: Code, websocket: WebSocket, id: ObjectId = Header(...)):
    """
    API to join a game

    :param code: Code of the game the client wants to join
    :param websocket: The websocket that the client is connecting on
    :param id: The ID of the user that wants to connect
    """
    user: User = await get_user_by_id(id)
    game: GameManager = playground.get_game(code)

    await websocket.accept()
    await game.add_player(user, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await game.handle_json(user, data)
    except WebSocketDisconnect:
        # Client disconnected
        await game.handle_disconnect(user)
