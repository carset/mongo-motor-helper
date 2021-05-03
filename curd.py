# -*- encoding:utf-8 -*-
# :Date 2021/5/3
import uuid

from motor import motor_asyncio

from .base import CURDGeneric
from .model import user


class UserCURD(CURDGeneric[user.User]):

    async def unique_username(self,
                              name: str,
                              db: motor_asyncio.AsyncIOMotorClient) -> str:
        username = f"{name}{uuid.uuid4().hex[:8]}"
        if await self.inject(db).count_documents({'username': username}) == 0:
            return username
        return await self.unique_username(name=name)


curd = UserCURD()