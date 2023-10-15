from datetime import datetime

from bson import ObjectId
from bson.errors import InvalidId
from pydantic import BaseConfig, BaseModel


class OID(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        try:
            return ObjectId(str(v))
        except InvalidId:
            msg = 'Not a valid ObjectId'
            raise ValueError(msg)


class MongoModel(BaseModel):
    class Config(BaseConfig):
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            ObjectId: lambda oid: str(oid),
        }
