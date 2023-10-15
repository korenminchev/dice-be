"""Separated dependencies module. This is used instead of adding to __main__.py to prevent cyclic imports."""

from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine

from dice_be.managers.playground import Playground

client = AsyncIOMotorClient("mongodb://mongodb:27017/")
engine = AIOEngine(client=client, database="dice")
playground = Playground()
