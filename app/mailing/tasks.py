from __future__ import absolute_import, unicode_literals
from celery.utils.log import get_task_logger
from mailing.filters import MailingFilter
from mailing.models import Mailing, Message
from mailing.schemas import MessageSchemas
from app.celery import app as celery_app
from mailing.utils import get_timezone_current_time

logger = get_task_logger(__name__)


@celery_app.task(serializer="json")
def create_message_objects(mailing_id: int) -> list[MessageSchemas.MessageRequestFull]:

    """Receives ID of mailing.models.Mailing
    object and returns a list of  created messages in schema format"""

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


@celery_app.task(serializer="json", acks_late=False)
def send_message_object(message: MessageSchemas.MessageRequestFull):
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

    message = MessageSchemas.MessageRequest(
        id=message.id,
        text=message.mailing.text,
        phone=message.client.phone_number,
    )
    
    logger.info(f"Simulating sending {type(message)} {message} to third party serivce")