"""
Models for games and game metadata
"""
import random
from enum import Enum
from typing import TypeAlias, List, Literal

from pydantic import conint, PositiveInt

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
    name: str = ''
    dice: List[Dice] = []
    mistakes: PositiveInt = 0

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
    event: Literal['game_update'] = 'game_update'
    code: Code
    progression: GameProgression = GameProgression.LOBBY
    rules: GameRules = GameRules()
    players: dict[OID, PlayerData] = {}

    def add_player(self, player_id: OID, player_name: str):
        self.players[player_id] = PlayerData(name=player_name)

    def lobby_json(self) -> str:
        return self.json(exclude={'players': {'__all__': {'dice', 'mistakes'}}})

    def player_update_json(self) -> str:
        return self.json(include={'event': True, 'players': {'__all__': {'name'}}})
