import os
import asyncio
from typing import Any, Optional
from aiohttp import ClientSession
from mailing.schemas import MessageSchemas


class SenderInterface:
    @classmethod
    async def send_single(cls, data: dict):
        """Sends one data package to third party service"""
        raise NotImplementedError


class ProbeSender(SenderInterface):

    CLIENT_ENDPOINT_URL = "https://probe.fbrq.cloud/v1/"

    @classmethod
    def get_jwt_key(cls, *args, **kwargs):
        return os.environ.get("THIRD_PARTY_JWT_KEY")

    @classmethod
    async def send_single(cls, data: MessageSchemas.MessageRequest) -> Optional[dict]:

        target_url: str = ProbeSender.CLIENT_ENDPOINT_URL + f"send/{data.id}"
        async with ClientSession() as session:
            headers = {
                "Authorization": ProbeSender.get_jwt_key(),
                "Content-Type": "application/json",
            }
            try:
                async with session.post(
                    url=target_url, data=data.dict(), headers=headers
                ) as response:
                    return await response.json(content_type="text/json")
            except Exception as e:
                print(f"[LOG] -> Error sending data: {e}")
                return None

    @classmethod
    def response_valid(cls, response: dict) -> bool:
        return response and "code" in response
