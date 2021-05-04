# -*- encoding:utf-8 -*-
# :Date 2021/5/2
from datetime import datetime
from functools import lru_cache
from typing import TypeVar, Generic, List, ClassVar, Any

import bson
from motor import motor_asyncio
from pydantic import BaseModel, BaseConfig
from pymongo import IndexModel

T = TypeVar('T', bound='Model')


def swap(obj: Any, x: str, y: str):
    if isinstance(obj, dict):
        if x in obj and y not in obj:
            obj[y] = obj.pop(x)
        return {
            k: swap(v, x, y) for k, v in obj.items()
        }
    elif isinstance(obj, list):
        return [
            swap(v, x, y) for v in obj
        ]
    return obj


def camel_to_snake(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


class ObjectId(bson.ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not bson.ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return bson.ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class Model(BaseModel):
    __tablename__: ClassVar[str]
    __indexes__: ClassVar[List[IndexModel]]

    class Config(BaseConfig):
        orm_mode = True
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            bson.ObjectId: lambda oid: str(oid),
        }

    @staticmethod
    def swap(obj: Any, x: str, y: str) -> Any:
        return swap(obj, x, y)

    def __init_subclass__(cls, **kwargs):
        if getattr(cls, '__tablename__', None) is None:
            setattr(cls, '__tablename__', cls.__name__.lower())
            # setattr(cls, '__tablename__', camel_to_snake(cls.__name__))


class CURDGeneric(Generic[T]):
    @classmethod
    @lru_cache  # cache_clear()
    def get_item(cls):
        item = getattr(cls, '__orig_bases__')[0].__args__[0]
        return item

    def __getattr__(self, item, *args, **kwargs):
        return self

    @property
    def tablename(self):
        return getattr(self.get_item(), '__tablename__')

    @classmethod
    async def create_index(cls, db: motor_asyncio.AsyncIOMotorClient):
        model = cls.get_item()
        indexes = [x for x in getattr(model, '__indexes__')]
        tbl = getattr(model, '__tablename__')
        return await db[tbl].create_indexes(indexes)

    def inject(self, db: motor_asyncio.AsyncIOMotorClient) -> motor_asyncio.AsyncIOMotorCollection:
        return db[self.tablename]
