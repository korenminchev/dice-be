from typing import Literal, Union, List

from pydantic import BaseModel, Field

from dice_be.models.games import PlayerData, Dice
from dice_be.models.utils import OID, MongoModel


class GameJoin(MongoModel):
    """
    # TODO: Change this to lobby update
    Signals that a new player joined the game
    Broadcast from server
    """
    event: Literal['game_join']
    joined_player_id: OID


class GameStart(BaseModel):
    """
    Signals that the game has started
    Sent from the host to the server
    """
    event: Literal['game_start']


class RoundStart(MongoModel):
    event: Literal['round_start']
    player_dice: List[Dice]

    @classmethod
    def from_player(cls, player: PlayerData):
        return cls(event='round_start', player_dice=player.dice)


class Accusation(MongoModel):
    accuser: OID
    accused: OID
    die_value: int
    dice_count: int

class Event(MongoModel):
    __root__: Union[GameJoin, GameStart, RoundStart] = Field(..., discriminator='event')

