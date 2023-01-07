from pydantic import BaseModel
from datetime import datetime


class TagSchema(BaseModel):
    value: str


class OperatorSchema(BaseModel):
    name: str
    code: str


class UserChemas:
    class MailingUser(BaseModel):
        id: int
        phone_number: int
        operator: OperatorSchema
        time_zone: str


class MailingSchemas:
    class MailingSchema(BaseModel):
        id: int
        text: str
        start_time: datetime
        end_time: datetime


class MessageSchemas:
    class MessageRequestBase(BaseModel):
        id: int

    class MessageRequest(MessageRequestBase):
        text: str
        phone: int

    class MessageRequestFull(MessageRequestBase):
        status: str
        mailing: MailingSchemas.MailingSchema
        client: UserChemas.MailingUser
