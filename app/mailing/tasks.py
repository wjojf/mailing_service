from __future__ import absolute_import, unicode_literals
from typing import Any, Optional
from celery.utils.log import get_task_logger
from mailing.filters import MailingFilter
from mailing.models import Mailing, Message, update_message_status
from mailing.schemas import MessageSchemas
from app.celery import app as celery_app
from mailing.utils import get_timezone_current_time
from mailing.thrid_party import ProbeSender
import asyncio

logger = get_task_logger(__name__)



@celery_app.task(serializer="json")
def create_message_objects(mailing_id: int) -> list[MessageSchemas.MessageRequestFull]:

    try:
        mailing_obj = Mailing.objects.get(id=mailing_id)
    except Exception as exc:
        logger.info(f"[LOG] -> Error extracting Mailing object: {exc}")
        return []

    filtered_clients = MailingFilter.filter_queryset(mailing_obj=mailing_obj)
    if not filtered_clients:
        logger.info("Could not filter clients")
        return []

    logger.info(f"Filtered Clients: {filtered_clients}")

    messages = []
    for client in filtered_clients:
        message_obj, created = Message.objects.get_or_create(
            client=client, mailing=mailing_obj
        )
        logger.info(f"[LOG] -> Created Message {message_obj}")
        if created:
            messages.append(message_obj.to_message_request().dict())
            message_obj.save()

    return messages


@celery_app.task(serializer="json")
def set_message_status(message_id: int) -> None:
    logger.info(f"Setting message status. Received ID: {message_id}")
    update_message_status(message_id=message_id)
    logger.info(f"Sucessfully set status in database for Message {message_id}")


@celery_app.task(serializer="json", acks_late=False)
def send_message_object(message: dict) -> Optional[dict]:
    def is_valid_time_to_send(message: MessageSchemas.MessageRequestFull) -> bool:
        return (
            message.mailing.start_time
            <= get_timezone_current_time(message.client.time_zone)
            <= message.mailing.end_time
        )

    message = MessageSchemas.MessageRequestFull(**message)
    if not is_valid_time_to_send(message):
        logger.info(f"Mailing already finished {message}")
        return False

    message_request = MessageSchemas.MessageRequest(
        id=message.id,
        text=message.mailing.text,
        phone=message.client.phone_number,
    )

    logger.info(f"Sending {message_request} to third party serivce")

    third_party_response = asyncio.run(ProbeSender.send_single(data=message_request))

    if not ProbeSender.response_valid(third_party_response):
        logger.info(f"Error sending {message}")
        return

    logger.info(f"Sucessfully sent {message_request}")
    logger.info(f"Received Response: {third_party_response}")

    set_message_status.delay(message_request.id) # call another task to update db status

    return third_party_response


