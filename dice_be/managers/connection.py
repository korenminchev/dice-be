"""
Connection management
"""

from odmantic import ObjectId
from starlette.websockets import WebSocket

from dice_be.models.users import User


class ConnectionManager:
    """
    Connection manager is responsible for handling all client connections in a single game
    """

    def __init__(self):
        self.connections: dict[ObjectId, WebSocket] = {}

    def __getitem__(self, client: User) -> WebSocket:
        return self.connections.__getitem__(client.id)

    async def add_connection(self, client: User, connection: WebSocket):
        """
        Registered a new client
        """
        await connection.accept()
        self.connections[client.id] = connection

    def remove_connection(self, client: User):
        """
        Unregisters a client, by the time this is called - nothing is sent on the websocket, the client is assumed
        to be already disconnected
        """
        del self.connections[client.id]
