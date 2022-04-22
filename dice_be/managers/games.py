from fastapi import WebSocket

from ..models.games import GameData, Code
from ..models.users import User
from .connection import ConnectionManager


class GameManager:
    def __init__(self, code: Code):
        self.game_data = GameData(code=code)
        self.connection_manager = ConnectionManager()

    async def add_player(self, player: User, connection: WebSocket):
        self.game_data.players.append(player.id)
        await self.connection_manager.add_connection(player, connection)

    async def handle_json(self, player: User, data: dict):
        pass

    async def handle_disconnect(self, player: User):
        self.connection_manager.remove_connection(player)
