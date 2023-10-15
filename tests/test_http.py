import pytest

from fastapi.testclient import TestClient

from dice_be.__main__ import app
from dice_be.models.games import Code, GameRules, GameData, GameProgression

@pytest.fixture
def http_client():
    return TestClient(app)


@pytest.fixture
def game(http_client: TestClient):
    raw_code = http_client.post('/games/', json={'game_rules': dict(GameRules())})
    game_code = Code(raw_code.json())
    game_info = http_client.get(f'/games/{game_code}')
    return GameData(**game_info.json())


def test_game_creation(game: GameData):
    assert game.event == 'game_update'
    assert len(game.code) == 4 and game.code.isnumeric()
    assert game.progression == GameProgression.LOBBY == 'lobby'
