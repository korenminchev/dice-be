"""
Game logic management
"""
import asyncio

from fastapi import WebSocket

from dice_be.models.games import GameData, Code, GameProgression
from dice_be.models.users import User
from dice_be.models.game_events import Event
from dice_be.managers.connection import ConnectionManager


class GameManager:
    """
    Manages the progression of a single game
    """
    def __init__(self, code: Code):
        self.game_data = GameData(code=code)
        self.connection_manager = ConnectionManager()

    async def add_player(self, player: User, connection: WebSocket):
        """
        Add a player to the game
        """
        self.game_data.add_player(player.id, player.name)
        await self.connection_manager.add_connection(player, connection)

        await asyncio.gather(
            self.connection_manager.send(player.id, self.game_data.lobby_json()),
            self.connection_manager.broadcast(
                self.game_data.player_update_json(),
                exclude_ids={player.id}
            )
        )

    async def handle_json(self, player: User, data: dict):
        """
        Handles a json received from the player's connection
        :param player: The player who sent the data
        :param data: Parsed json object
        """
        event = Event.parse_obj(data).__root__

        # match event.data:
        #     case GameStart(event.data):
        #         await self.handle_game_start()
        #         return

    async def handle_disconnect(self, player: User):
        """
        Handle a player issued disconnect
        :param player: The player that disconnected
        """
        self.connection_manager.remove_connection(player)

    async def handle_game_start(self):
        self.game_data.progression = GameProgression.IN_GAME
        # await self.connection_manager.broadcast()
