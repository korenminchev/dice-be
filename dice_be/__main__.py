from fastapi import FastAPI

from .exceptions import IDNotFound, GameNotFound
from .routers import users, games

app = FastAPI()
app.include_router(users.router)
app.include_router(games.router)

app.add_exception_handler(IDNotFound, IDNotFound.handler)
app.add_exception_handler(GameNotFound, GameNotFound.handler)