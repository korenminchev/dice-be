from odmantic import ObjectId
from starlette.websockets import WebSocket

from ..models.users import User


class ConnectionManager:
    def __init__(self):
        self.connections: dict[ObjectId, WebSocket] = {}

    def __getitem__(self, client: User) -> WebSocket:
        return self.connections.__getitem__(client.id)

    async def add_connection(self, client: User, connection: WebSocket):
        await connection.accept()
        self.connections[client.id] = connection

    def remove_connection(self, client: User):
        del self.connections[client.id]
