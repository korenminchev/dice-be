"""
Handle all game related API
"""

from fastapi import APIRouter, WebSocket
from bson import ObjectId
from starlette.websockets import WebSocketDisconnect

from dice_be.routers.users import get_user_by_id
from dice_be.dependencies import playground
from dice_be.exceptions import GameNotFound
from dice_be.managers.games import GameManager
from dice_be.models.games import Code, GameData, GameProgression
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
    Gets all the info about a game
    """
    return playground.get_game(code).game_data

@router.get('/{code}/state', response_model=GameProgression, responses=GameNotFound.response())
async def get_game_state(code: str):
    """
    Gets the state of a game, use this before attempting to join
    """
    return playground.get_game(code).game_data.progression

@router.get('/{code}/{user_id}}', response_model=bool, responses=GameNotFound.response())
async def check_player_in_game(code: str, user_id: ObjectId):
    """
    Checks if the player is in the game
    """
    return user_id in playground.get_game(code).player_mapping

# pylint:disable=redefined-builtin, invalid-name
@router.websocket("/{code}/ws/")
async def websocket_endpoint(code: Code, websocket: WebSocket):
    """
    API to join a game

    :param code: Code of the game the client wants to join
    :param websocket: The websocket that the client is connecting on
    """
    await websocket.accept()

    user_id = (await websocket.receive_json())['id']

    user: User = await get_user_by_id(ObjectId(user_id))
    game: GameManager = playground.get_game(code)

    await game.handle_connect(user, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await game.handle_json(user, data)
    except WebSocketDisconnect:
        # Client disconnected
        await game.handle_disconnect(user)
