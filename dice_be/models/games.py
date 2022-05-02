"""
Models for games and game metadata
"""
from enum import Enum
from typing import TypeAlias, List

from odmantic import Model, ObjectId

Code: TypeAlias = str

# pylint: disable=abstract-method
class GameState(str, Enum):
    """
    Represents the current state of the game
    """
    LOBBY = 'lobby'
    IN_GAME = 'in game'


# pylint: disable=abstract-method
class GameData(Model):
    """
    Data of an active game
    """
    code: Code
    state: GameState
    players: List[ObjectId] = []
