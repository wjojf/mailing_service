from rest_framework import serializers
import mailing.models as models


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = "__all__"


class OperatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Operator
        fields = "__all__"


class ClientBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Client
        fields = "__all__"


class ClientSerializer(ClientBasicSerializer):
    operator = OperatorSerializer(read_only=True)


class ClientFilterBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ClientFilter
        fields = "__all__"


class ClientFilterSerializer(ClientFilterBasicSerializer):
    tags = TagSerializer(many=True, read_only=True)
    operators = OperatorSerializer(many=True, read_only=True)


class MailingBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Mailing
        fields = '__all__'


class MailingSerializer(MailingBasicSerializer):
    client_filter = ClientFilterSerializer(read_only=True)


class MessageBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Message
        fields = '__all__'


class MessageSerializer(MessageBasicSerializer):
    mailing = MailingSerializer(read_only=True)
    client = ClientSerializer(read_only=True)
