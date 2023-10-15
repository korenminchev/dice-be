"""This module handles multiple concurrent games - hence playground."""

from random import randint

from dice_be.exceptions import GameNotFound
from dice_be.managers.games import GameManager
from dice_be.models.games import Code, GameRules


class Playground:
    """Create and store concurrent games.

    Games are NOT stored in a DB
    """

    def __init__(self) -> None:
        self.current_games: dict[Code, GameManager] = {}

    def create_game(self, game_rules: GameRules) -> Code:
        """Creates a new game in the playground
        :return: The code of the game (used for joining).
        """
        code = self._generate_code()
        self.current_games[code] = GameManager(code, game_rules)
        return code

    def delete_game(self, code: Code):
        """Delete a game from the playground by its code."""
        del self.current_games[code]

    def get_game(self, code: Code) -> GameManager:
        """Retrieve a game by its code."""
        if code not in self.current_games:
            raise GameNotFound(code)

        return self.current_games[code]

    def _generate_code(self) -> Code:
        code = f"{randint(1, 9999):04}"

        while code in self.current_games:
            code = f"{randint(1, 9999):04}"

        return code
