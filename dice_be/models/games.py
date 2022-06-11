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
    current_dice_count: PositiveInt = 0
    ready: bool = False
    left_player_id: OID = None
    right_player_id: OID = None

    def roll_dice(self) -> 'PlayerData':
        self.dice = [random.randint(1, 6) for _ in range(self.current_dice_count)]
        return self


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

    def add_player(self, player: User):
        self.players.append(player := PlayerData(id=player.id, name=player.name))
        return player

    def remove_player(self, player: User):

        for p in self.players:
            if player.id == p.id:
                # It's probably ok to remove values while iterating over the list because we return right after
                return self.players.remove(p)

    def lobby_json(self, *data_filter) -> str:
        includes = {'event', 'progression', 'rules', 'players'}

        if not data_filter:
            return self.json(include=includes)

        return self.json(include=includes & (set(data_filter) | {'event'}))

    def player_update_json(self) -> str:
        return self.json(include={'event': True, 'players': {'__all__': {'id', 'name', 'ready'}}})

    def start_game_json(self) -> str:
        return self.json(include={'event': True, 'rules': True})

    def round_start_json(self) -> str:
        return self.json(include={
            'event': True,
            'players': {'__all__': {'id', 'name', 'current_dice_count'}},
        })
