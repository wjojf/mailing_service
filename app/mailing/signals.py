from mailing.models import Mailing
from mailing.filters import MailingFilter
from mailing.tasks import create_message_objects, send_message_objects
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver


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
        print("[LOG] -> HANDLING POST CREATE")
        instance = kwargs["instance"]

        if not instance:
            return

        print(instance.id)
        messages = list(create_message_objects.delay(int(instance.id)).collect())
        '''FIXME: indexing is hardcode and can be crashed'''
        messages = [m[1][0] for m in messages] 
        print(f"[LOG] -> Received messages: {type(messages)}: {messages}")
        send_message_objects.delay(messages)
