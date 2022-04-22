from typing import List

from fastapi import APIRouter, Body
from odmantic import ObjectId

from ..exceptions import IDNotFound
from ..models.users import User
from ..dependencies import engine as db

router = APIRouter(
    prefix='/users',
    tags=["Users"],
)


async def get_user_by_id(id: ObjectId) -> User:
    if user := await db.find_one(User, User.id == id):
        return user
    raise IDNotFound(User, id)


@router.get('/', response_model=list[User])
async def get_all_users():
    return await db.find(User)


@router.post('/', response_model=User)
async def create_user(name: str = Body(..., embed=True)):
    return await db.save(User(name=name))


@router.get('/{id}', response_model=User, responses=IDNotFound.response())
async def get_user_by_id_endpoint(id: ObjectId):
    return await get_user_by_id(id)


@router.post('/{id}/friends', response_model=User, responses=IDNotFound.response())
async def add_friends(id: ObjectId, friends: List[ObjectId]):
    user = await get_user_by_id(id)
    user.friend_ids.extend(friends)
    await db.save(user)
    return user

