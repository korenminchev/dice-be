from typing import TypeAlias, List

from odmantic import Model, ObjectId

Code: TypeAlias = str


# noinspection PyAbstractClass
class GameData(Model):
    code: Code
    players: List[ObjectId] = []
