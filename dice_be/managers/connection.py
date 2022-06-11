"""
Connection management
"""
import asyncio
import json
from typing import Iterable

from odmantic import ObjectId
from pydantic import BaseModel
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

    def add_connection(self, client: User, connection: WebSocket):
        """
        Registered a new client, assumes the connection is already accepted
        """
        self.connections[client.id] = connection

    async def disconnect(self, client: User):
        """
        Explicitly disconnect a client
        """
        await self.connections[client.id].close()

    def remove_connection(self, client: User):
        """
        Unregisters a client, by the time this is called - nothing is sent on the websocket,
        which is assumed to be already closed
        """
        del self.connections[client.id]

    async def send(self, client: User, data: str | dict | BaseModel):
        if isinstance(data, dict):
            data = json.dumps(data)
        elif isinstance(data, BaseModel):
            data = data.json()
        
        print(f"Sending to {client.id}, {client.name}: {data}")
        await self.connections[client.id].send_text(data)

    async def broadcast(self, data: str | dict, *, exclude: Iterable[User] = ()):
        """
        Broadcast a message to all clients
        """
        exclude_ids = set(user.id for user in exclude)
        
        print(f"Broadcasting {data}")

        if isinstance(data, dict):
            data = json.dumps(data)

        await asyncio.gather(
            *(connection.send_text(data)
              for client, connection in self.connections.items() if client not in exclude_ids)
        )
