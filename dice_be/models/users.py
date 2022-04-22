from typing import List

from odmantic import Model, ObjectId


# noinspection PyAbstractClass
class User(Model):
    name: str
    friend_ids: List[ObjectId] = []
