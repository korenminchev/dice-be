from http import HTTPStatus

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .models.games import Code


class NotFoundHttpError(LookupError):
    response_code = HTTPStatus.NOT_FOUND.value

    @staticmethod
    async def handler(request: Request, exc):
        return JSONResponse(
            status_code=NotFoundHttpError.response_code,
            content={'detail': str(exc)},
        )

    class ResponseModel(BaseModel):
        detail: str

    @classmethod
    def response(cls):
        return {cls.response_code: {"model": cls.ResponseModel}}


class IDNotFound(NotFoundHttpError):

    def __init__(self, model, id):
        self.model = model
        self.id = id

    def __str__(self):
        return f'Unable to find {self.model.__name__} with ID {self.id}'


class GameNotFound(NotFoundHttpError):
    def __init__(self, code: Code):
        self.code = code

    def __str__(self):
        return f'Unable to find any game with the code {self.code}'
