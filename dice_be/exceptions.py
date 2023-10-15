"""Custom exceptions."""
from http import HTTPStatus

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from dice_be.models.games import Code


class NotFoundHttpError(LookupError):
    """Base Exception for 404 NOT FOUND errors."""

    response_code = HTTPStatus.NOT_FOUND.value

    class ResponseModel(BaseModel):
        """Response model used in the FastAPI exception handler."""

        detail: str

    @staticmethod
    async def handler(_: Request, exc) -> JSONResponse:
        """Exception handler for FastAPI
        :param _: The request from the client (unused)
        :param exc: The exception object that was raised
        :return: 404 NOT FOUND response with error details.
        """
        return JSONResponse(
            status_code=NotFoundHttpError.response_code,
            content=NotFoundHttpError.ResponseModel(detail=str(exc)).dict(),
        )

    @classmethod
    def response(cls):
        """Response information, used for OpenAPI documentation."""
        return {cls.response_code: {"model": cls.ResponseModel}}


class IDNotFound(NotFoundHttpError):
    """Exception that is raised when and ID of a specific model isn't found in the DB."""

    # pylint:disable=redefined-builtin, invalid-name
    def __init__(self, model, id) -> None:
        self.model = model
        self.id = id
        super().__init__()

    def __str__(self) -> str:
        return f"Unable to find {self.model.__name__} with ID {self.id}"


class GameNotFound(NotFoundHttpError):
    """Exception that is raised when a specific game is not found
    This differs from 'IDNotFound' because active games aren't saved in the DB.
    """

    def __init__(self, code: Code) -> None:
        self.code = code
        super().__init__()

    def __str__(self) -> str:
        return f"Unable to find any game with the code {self.code}"
