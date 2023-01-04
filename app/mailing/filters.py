from mailing.models import Mailing, Client
from typing import Optional


class MailingFilter:

    @classmethod
    def filter_queryset(cls, mailing_obj: Mailing, user_qs=Client.objects.all()):
        '''Filters Clients queryset by tags and operators'''

        if not mailing_obj.client_filter or not user_qs:
            return

        filter_operators = mailing_obj.client_filter.operators.all()

        if len(filter_operators) > 0:
            user_qs = user_qs.filter(                                                                                                                                                                                                                                                                                                                                                                                   
                operator__in=filter_operators)                                                                                                                                                      

        tags = mailing_obj.client_filter.tags.all()
        if len(tags) > 0:
            user_qs = user_qs.filter(tags__tag__in=tags)

        return user_qs
