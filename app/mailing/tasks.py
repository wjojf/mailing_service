from __future__ import absolute_import, unicode_literals
from celery.utils.log import get_task_logger
from mailing.filters import MailingFilter
from mailing.models import Mailing, Message
from mailing.schemas import MessageSchemas
from app.celery import app as celery_app


logger = get_task_logger(__name__)


@celery_app.task(serializer="json")
def create_message_objects(mailing_id: int) -> list[MessageSchemas.MessageRequest]:

    """Receives ID of mailing.models.Mailing
    object and returns a list of  created messages in schema format"""

    print("[LOG] -> Received id: {mailing_id}")
    
    try:
        mailing_obj = Mailing.objects.get(id=mailing_id)
    except Exception as exc:
        print(f"[LOG] -> Error extracting Mailing object: {exc}")
        return []

    filtered_clients = MailingFilter.filter_queryset(mailing_obj=mailing_obj)
    if not filtered_clients:
        print(f"[LOG] -> Could not filter clients")
        return []

    print(f"[LOG] -> Filtered Clients: {filtered_clients}")

    messages = []
    for client in filtered_clients:
        message_obj, created = Message.objects.get_or_create(
            client=client, mailing=mailing_obj
        )
        print(f"[LOG] -> Created Message {message_obj}")
        if created:
            messages.append(message_obj.to_message_request().dict())
            message_obj.save()

    return messages


@celery_app.task(serializer="json")
def send_message_objects(
    messages: list[MessageSchemas.MessageRequest],
) -> list[MessageSchemas.MessageRequest]:

    for message in messages:
        print(f"Simulating sending {message} to third party serivce")

    return messages
