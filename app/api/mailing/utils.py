from mailing import models as models
from mailing.schemas import MessageSchemas, MailingSchemas
from typing import Any


def group_messages_by_status(
    messages: list[MessageSchemas.MessageRequestFull],
) -> dict[str, dict[str, Any]]:
    
    messages_groupped = {}
    for message in messages:
        if message.status in messages_groupped.keys():
            messages_groupped[message.status]["messages"].append(message.dict())
            messages_groupped[message.status]["count"] += 1

        else:
            messages_groupped[message.status] = {"count": 1, "messages": [message.dict()]}

    return messages_groupped


def get_messages_stats(
    messages: list[MessageSchemas.MessageRequestFull],
) -> dict:
    
    messages_groupped = group_messages_by_status(messages=messages)
    return {
        "data": messages_groupped,
        "meta": {
            "status": 200 if messages_groupped else 404,
            "message": "OK" if messages_groupped else "Error"
        }
    }
