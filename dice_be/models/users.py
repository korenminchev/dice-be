"""
Models for users data
"""

from typing import List

from odmantic import Model, ObjectId


# pylint: disable=abstract-method
class User(Model):
    """
    User data, this class defines how users are saved in the DB
    """
    name: str
    friend_ids: List[ObjectId] = []
