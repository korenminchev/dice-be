import json

import pytest
from pydantic import ValidationError

from dice_be.models.game_events import Event, RoundStart
from dice_be.models.games import PlayerData, GameData


def test_round_start():
    pd = PlayerData(dice=[1, 2, 3])
    m = RoundStart.from_player(pd)
    assert json.loads(m.json())['dice']


def test_strict_pydantic():
    j = {'player_dice': [1, 2, 3]}
    with pytest.raises(ValidationError):
        _ = Event.parse_obj(j)


def test_game_data():
    gd = GameData(event='game_update', code=1234, players=[PlayerData(dice=[1, 2, 3]), PlayerData(dice=[4, 5, 6])])
    player_update_dict = json.loads(gd.player_update_json())
    assert player_update_dict['event'] == 'game_update'
    assert all('name' in p for p in player_update_dict['players'])
    assert all('id' in p for p in player_update_dict['players'])
    assert all('dice' not in p for p in player_update_dict['players'])

    lobby_json = json.loads(gd.lobby_json('players'))
    assert lobby_json['event'] == 'game_update'
    assert 'rules' not in lobby_json
    assert all('dice' not in p for p in player_update_dict['players'])

