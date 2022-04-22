from fastapi import WebSocket

from ..models.games import GameData
from ..models.users import User
from .connection import ConnectionManager


class GameManager:
    def __init__(self):
        self.game_data = GameData()
        self.players: list[User] = []
        self.connection_manager = ConnectionManager()

    async def add_player(self, player: User, connection: WebSocket):
        self.players.append(player)
        await self.connection_manager.add_connection(player, connection)

    async def handle_json(self, player: User, data: dict):
        pass

    async def handle_disconnect(self, player: User):
        self.connection_manager.remove_connection(player)
