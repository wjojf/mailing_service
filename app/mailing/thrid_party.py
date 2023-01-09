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
    CLIENT_SEND_MESSAGE_URL = CLIENT_ENDPOINT_URL + "send/{msgID}"
    N_RETRIES = 5 
    RETRY_DELAY_SECONDS = 1

    @classmethod
    def get_jwt_key_header(cls, *args, **kwargs):
        return "Bearer " + os.environ.get("THIRD_PARTY_JWT_KEY")

    @classmethod
    async def send_single(cls, data: MessageSchemas.MessageRequest) -> Optional[dict]:

        target_url: str = ProbeSender.CLIENT_SEND_MESSAGE_URL.format(msgID=data.id)
    
        async with ClientSession() as session:
            headers = {
                "Authorization": ProbeSender.get_jwt_key_header(),
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            retries = 0
            
            while retries < ProbeSender.N_RETRIES:
                
                try:
                    async with session.post(
                        url=target_url, data=data.json(), headers=headers
                    ) as response:
                        return await response.json()
                except Exception as e:
                    print(f"[LOG] -> Error sending {data}: {e}")
                    asyncio.sleep(ProbeSender.RETRY_DELAY_SECONDS)
                    retries += 1
            
            return None
                    

    @classmethod
    def response_valid(cls, response: dict) -> bool:
        return response and "code" in response
