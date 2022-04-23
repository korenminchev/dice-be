"""
Game logic management
"""

from fastapi import WebSocket

from dice_be.models.games import GameData, Code
from dice_be.models.users import User
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
        Add a plyer to the game
        """
        self.game_data.players.append(player.id)
        await self.connection_manager.add_connection(player, connection)

    async def handle_json(self, player: User, data: dict):
        """
        Handles a json received from the player's connection
        :param player: The player who sent the data
        :param data: Parsed json object
        """
        raise NotImplementedError

    async def handle_disconnect(self, player: User):
        """
        Handle a player issued disconnect
        :param player: The player that disconnected
        """
        self.connection_manager.remove_connection(player)
