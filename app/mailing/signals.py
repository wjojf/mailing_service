from mailing.models import Mailing
from mailing.tasks import create_message_objects, send_message_object
from mailing.utils import alter_datetime_timezone, get_closer_date, get_utc_start_time
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime
from dateutil import parser as date_parser


def on_transaction_commit(func):
    def inner(*args, **kwargs):
        transaction.on_commit(lambda: func(*args, **kwargs))

    return inner


class SignalHandler:
    @staticmethod
    def handle_pre_save(sender, **kwargs):
        raise NotImplementedError

    @staticmethod
    def handle_post_save(sender, **kwargs):
        raise NotImplementedError

    @staticmethod
    def handle_pre_update(sender, **kwargs):
        raise NotImplementedError

    @staticmethod
    def handle_post_update(sender, **kwargs):
        raise NotImplementedError

    @staticmethod
    def handle_pre_delete(sender, **kwargs):
        raise NotImplementedError

    @staticmethod
    def handle_post_delete(sender, **kwargs):
        raise NotImplementedError


class MailingHandler(SignalHandler):
    @staticmethod
    @receiver(post_save, sender=Mailing)
    @on_transaction_commit
    def handle_post_save(sender, **kwargs):
        instance = kwargs["instance"]  # Mailing object

        if not instance:
            return

        # FIXME: catch exceptions
        try:
            messages = list(create_message_objects.delay(int(instance.id)).collect())
            messages = [m[1][0] for m in messages]  # FIXME: hardcode
        except Exception:
            return

        print(f"[LOG] -> Received messages: {type(messages)}: {messages}")

        for message in messages:
            message_eta = get_utc_start_time(
                get_closer_date(
                    alter_datetime_timezone(
                        instance.start_time, message["client"]["time_zone"]
                    ),
                    message["client"]["time_zone"],
                )
            )
            print("[LOG] -> UTC message ETA: {}".format(message_eta))
            send_message_object.apply_async(
                (message,),
                eta=message_eta,
                expires=alter_datetime_timezone(
                    dt=date_parser.parse(message["mailing"]["end_time"]),
                    timezone=message["client"]["time_zone"],
                ),
            )
            print(f"[LOG] -> Scheduled sending {message}")
