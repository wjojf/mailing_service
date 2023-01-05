import os
import asyncio
from aiohttp import ClientSession
from mailing.schemas import MessageChemas


class SenderInterface:
    @classmethod
    async def send_single(cls, data: dict):
        raise NotImplementedError

    @classmethod
    async def send_multiple(cls, instances: list[dict]):
        raise NotImplementedError


class ProbeSender(SenderInterface):

    CLIENT_ENDPOINT_URL = "https://probe.fbrq.cloud/v1"

    @classmethod
    def get_jwt_key(cls, *args, **kwargs):
        return os.environ.get("THIRD_PARTY_JWT_KEY")

    @classmethod
    async def send_single(cls, data: MessageChemas.MessageRequest):
        async with ClientSession() as session:
            headers = {"Authorization": ProbeSender.get_jwt_key()}

            async with session.post(
                url=ProbeSender.CLIENT_ENDPOINT_URL, data=data, headers=headers
            ) as response:
                return await response.json()
