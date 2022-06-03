"""
Connection management
"""
import asyncio
from typing import Iterable

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
        Registered a new client, assumes the connection is already accepted
        """
        self.connections[client.id] = connection

    def remove_connection(self, client: User):
        """
        Unregisters a client, by the time this is called - nothing is sent on the websocket, the client is assumed
        to be already disconnected
        """
        del self.connections[client.id]

    async def send(self, client: ObjectId, data: str):
        print('sending ')
        await self.connections[client].send_text(data)

    async def broadcast(self, data: str, *, exclude_ids=set[ObjectId]):
        """
        Broadcast a message to all clients
        """
        await asyncio.gather(
            connection.send_text(data) for client, connection in self.connections.values() if client not in exclude_ids
        )
