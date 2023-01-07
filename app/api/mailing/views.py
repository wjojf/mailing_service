from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import mailing.models as models
import api.mailing.serializers as serializers
from api.mailing.utils import get_messages_stats


class TagViewSet(ModelViewSet):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer


class OperatorViewSet(ModelViewSet):
    queryset = models.Operator.objects.all()
    serializer_class = serializers.OperatorSerializer


class ClientViewSet(ModelViewSet):
    queryset = models.Client.objects.select_related("operator").all()

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return serializers.ClientSerializer
        return serializers.ClientBasicSerializer


class MailingViewSet(ModelViewSet):
    queryset = models.Mailing.objects.select_related("client_filter").all()

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return serializers.MailingSerializer
        return serializers.ClientFilterBasicSerializer


@api_view(["GET"])
def mailing_statistics_view(request, pk):
    try:
        mailing: models.Mailing = models.Mailing.objects.get(pk=pk)
    except Exception as e:
        return Response(
            {
                "data": None,
                "meta": {
                    "error": "Could not get Mailing object with ID: {}".format(pk),
                    "error_message": e,
                },
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    mailing_messages: list[models.Message] = list(mailing.message_set.all())

    if not mailing_messages:
        return Response(
            {"data": None, "meta": {"error": f"Not messages sent for {str(mailing)}"}},
            status=status.HTTP_404_NOT_FOUND,
        )

    mailing_messages_schemas = [
        mailing_message.to_message_request() for mailing_message in mailing_messages
    ]

    stats_response = get_messages_stats(mailing_messages_schemas)

    return Response(
        data=stats_response,
        status=status.HTTP_200_OK
        if stats_response["meta"]["status"] == 200
        else status.HTTP_400_BAD_REQUEST,
    )
