from random import randint

from .games import GameManager
from ..exceptions import GameNotFound
from ..models.games import Code


class Playground:
    def __init__(self):
        self.current_games: dict[Code, GameManager] = {}

    def create_game(self) -> Code:
        code = self._generate_code()
        self.current_games[code] = GameManager()
        return code

    def end_game(self, code: Code):
        del self.current_games[code]

    def get_game(self, code: Code) -> GameManager:
        if code not in self.current_games:
            raise GameNotFound(code)

        return self.current_games[code]

    def _generate_code(self) -> Code:
        code = f'{randint(1, 9999):04}'

        while code in self.current_games.keys():
            code = f'{randint(1, 9999):04}'

        return code
