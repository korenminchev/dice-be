"""
Models for games and game metadata
"""

from typing import TypeAlias, List

from odmantic import Model, ObjectId

Code: TypeAlias = str


# pylint: disable=abstract-method
class GameData(Model):
    """
    Data of an active game
    """
    code: Code
    players: List[ObjectId] = []
