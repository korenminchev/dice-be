"""
Models for games and game metadata
"""
import random
from enum import Enum
from typing import TypeAlias, List, Literal

from bson import ObjectId
from pydantic import conint, PositiveInt, Field

from dice_be.models.users import User
from dice_be.models.utils import MongoModel, OID

Code: TypeAlias = str
Dice: TypeAlias = conint(ge=1, le=6)

# pylint: disable=abstract-method
class GameProgression(str, Enum):
    """
    Represents the current state of the game
    """
    LOBBY = 'lobby'
    IN_GAME = 'in_game'


class PlayerData(MongoModel):
    id: OID = Field(default_factory=lambda: OID(ObjectId()))
    name: str = ''
    dice: List[Dice] = []
    mistakes: PositiveInt = 0
    ready: bool = False

    def roll_dice(self, max_dice: int):
        self.dice = [random.randint(1, 6) for _ in range(max_dice - self.mistakes)]


class GameRules(MongoModel):
    initial_dice_count: int = 5
    paso_allowed: bool = True
    exact_allowed: bool = True


class GameData(MongoModel):
    """
    Data of an active game
    """
    event: Literal['game_update']
    code: Code
    progression: GameProgression = GameProgression.LOBBY
    rules: GameRules = GameRules()
    players: list[PlayerData] = []
    admin: PlayerData = None

    def add_player(self, player: User):
        self.players.append(player := PlayerData(id=player.id, name=player.name))
        return player

    def lobby_json(self) -> str:
        return self.json(exclude={'players': {'__all__': {'dice', 'mistakes'}},
                                  'admin': {'__all__': {'dice', 'mistakes'}}})

    def player_update_json(self) -> str:
        return self.json(include={'event': True, 'players': {'__all__': {'id', 'name', 'ready'}}})

    def progression_update_json(self) -> str:
        return self.json(include={'event', 'progression'})
