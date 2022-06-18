from enum import Enum
from typing import Literal, Union, List

from pydantic import Field

from dice_be.models.games import PlayerData, Dice, GameData, GameRules
from dice_be.models.utils import OID, MongoModel


class PlayerReady(MongoModel):
    """
    Signals to the server that the player is ready
    Broadcast from server
    """
    event: Literal['player_ready']
    ready: bool
    left_player_id: OID
    right_player_id: OID


class ReadyConfirm(MongoModel):
    event: Literal['ready_confirm'] = 'ready_confirm'
    success: bool
    error: str = None


class PlayerLeave(MongoModel):
    """
    Signals to the server that the player is leaving
    """
    event: Literal['player_leave']

class GameStart(MongoModel):
    event: Literal['game_start'] = 'game_start'
    rules: GameRules

class RoundStart(MongoModel):
    event: Literal['round_start'] = 'round_start'
    dice: List[Dice]

    @classmethod
    def from_player(cls, player: PlayerData):
        return cls(dice=player.dice)


class AccusationType(str, Enum):
    Standard = 'standard'
    Exact = 'exact'
    Paso = 'paso'

class Accusation(MongoModel):
    event: Literal['accusation']
    type: AccusationType
    accused_player: OID
    dice_value: int = None
    dice_count: int = None

class RoundEnd(MongoModel):
    event: Literal['round_end'] = 'round_end'
    winner: OID
    loser: OID
    correct_accusation: bool
    accusation_type: AccusationType
    dice_value: int = None
    dice_count: int = None
    joker_count: int = None
    players: list
class Event(MongoModel):
    __root__: Union[PlayerReady, PlayerLeave, Accusation] = Field(..., discriminator='event')

