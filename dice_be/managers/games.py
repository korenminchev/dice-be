"""
Game logic management
"""
import asyncio

from bson import ObjectId
from fastapi import WebSocket

from dice_be.models.games import GameData, Code, GameProgression, PlayerData
from dice_be.models.users import User
from dice_be.models.game_events import Event
from dice_be.managers.connection import ConnectionManager


class GameManager:
    """
    Manages the progression of a single game
    """
    def __init__(self, code: Code):
        self.game_data = GameData(event='game_update', code=code)
        self.player_mapping: dict[ObjectId, PlayerData] = {}
        self.connection_manager = ConnectionManager()

    async def handle_json(self, player: User, data: dict):
        """
        Handles a json received from the player's connection
        :param player: The player who sent the data
        :param data: Parsed json object
        """
        event = Event.parse_obj(data).__root__

        match event:
            case GameData():
                await self.handle_game_update(player, event)

    async def handle_connect(self, player: User, connection: WebSocket):
        # Add the connection so we can send data
        self.connection_manager.add_connection(player, connection)

        # Send the lobby data to the player
        await self.connection_manager.send(player, self.game_data.lobby_json())

        # This means that the player is new (not reconnecting)
        if player.id not in self.player_mapping:
            self.player_mapping[player.id] = PlayerData(id=player.id, name=player.name)
            self.game_data.add_player(player)

            await self.connection_manager.broadcast(
                self.game_data.player_update_json(),
                exclude=(player,)
            )

    async def handle_disconnect(self, player: User):
        """
        Handle a websocket disconnect
        :param player: The player that disconnected
        """
        self.connection_manager.remove_connection(player)

    async def handle_game_update(self, player: User, data: GameData):
        pass

    async def handle_game_start(self):
        self.game_data.progression = GameProgression.IN_GAME
        await self.connection_manager.broadcast(self.game_data.progression_update_json())
