from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from .exceptions import IDNotFound, GameNotFound
from .routers import users, games

app = FastAPI()
app.include_router(users.router)
app.include_router(games.router)

app.add_exception_handler(IDNotFound, IDNotFound.handler)
app.add_exception_handler(GameNotFound, GameNotFound.handler)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Dice",
        version="Pre-release",
        description="Dice Game",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://raw.githubusercontent.com/Koren13n/dice-fe/feature/home_page/assets/images/dice_logo.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
