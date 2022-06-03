import json

import pytest
from pydantic import ValidationError

from dice_be.models.game_events import Event, GameJoin, RoundStart
from dice_be.models.games import PlayerData, GameData


def test_game_join():
    j = {'event': 'game_join', 'joined_player_id': '628d3f09086ffea0571081b3'}
    m = Event.parse_obj(j).__root__
    assert type(m) == GameJoin
    assert json.loads(m.json()) == j

def test_round_start():
    pd = PlayerData(dice=[1, 2, 3])
    m = RoundStart.from_player(pd)
    assert json.loads(m.json())['player_dice']

def test_strict_pydantic():
    j = {'player_dice': [1, 2, 3]}
    with pytest.raises(ValidationError):
        _ = Event.parse_obj(j)

def test_game_data():
    gd = GameData(event='game_update', code=1234, players={})
    assert gd.player_update_dict() == {
        'event': 'game_update',
        'players': {},
    }
