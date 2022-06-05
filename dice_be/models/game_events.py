from typing import Literal, Union, List

from pydantic import Field

from dice_be.models.games import PlayerData, Dice, GameData
from dice_be.models.utils import OID, MongoModel


class PlayerReady(MongoModel):
    """
    Signals to the server that the player is ready
    Broadcast from server
    """
    event: Literal['player_ready']
    ready: bool
    player_on_left: OID
    player_on_right: OID


class ReadyConfirm(MongoModel):
    event: Literal['ready_confirm'] = 'ready_confirm'
    success: bool
    error: str = None


class PlayerLeave(MongoModel):
    """
    Signals to the server that the player is leaving
    """
    event: Literal['player_leave']

class RoundStart(MongoModel):
    event: Literal['round_start'] = 'round_start'
    player_dice: List[Dice]

    @classmethod
    def from_player(cls, player: PlayerData):
        return cls(player_dice=player.dice)


class Accusation(MongoModel):
    accuser: OID
    accused: OID
    die_value: int
    dice_count: int

class Event(MongoModel):
    __root__: Union[PlayerReady, PlayerLeave, GameData] = Field(..., discriminator='event')

