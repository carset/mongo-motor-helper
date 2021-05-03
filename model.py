# -*- encoding:utf-8 -*-
# :Date 2021/5/2
from datetime import datetime, date
from pymongo import IndexModel, ASCENDING, DESCENDING
from .base import Model


class User(Model):
    __indexes__ = [
        IndexModel([("open_id", ASCENDING)], unique=True, background=True),
        IndexModel([("username", ASCENDING)], unique=True, background=True)
    ]

    username: str
    open_id: str
    created_at: datetime = lambda: datetime.now()

