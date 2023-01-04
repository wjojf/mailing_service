from rest_framework.viewsets import ModelViewSet
import mailing.models as models
import api.mailing.serializers as serializers


class TagViewSet(ModelViewSet):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer


class OperatorViewSet(ModelViewSet):
    queryset = models.Operator.objects.all()
    serializer_class = serializers.OperatorSerializer


class ClientViewSet(ModelViewSet):
    queryset = models.Client.objects.select_related('operator').all()

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return serializers.ClientSerializer
        return serializers.ClientBasicSerializer


class MailingViewSet(ModelViewSet):
    queryset = models.Mailing.objects.\
        select_related("client_filter").all()

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return serializers.MailingSerializer
        return serializers.ClientFilterBasicSerializer
