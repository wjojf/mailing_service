from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from mailing.validators.phone import validate_phone
from mailing.utils import TIMEZONES_CHOICES, DEFAULT_TIMEZONE, alter_datetime_timezone
from mailing.schemas import MessageSchemas, MailingSchemas, UserChemas, OperatorSchema


class Tag(models.Model):
    value = models.CharField(max_length=255, unique=True, verbose_name="Tag Value")

    def __str__(self):
        return self.value


class ItemTag(models.Model):
    """Tag sticked to specific instance"""

    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()

    obj = GenericForeignKey("content_type", "object_id")

    class Meta:
        unique_together = ("tag", "content_type", "object_id")

    def __str__(self):
        return f"{self.tag} -> {self.obj}"


class Operator(models.Model):
    name = models.CharField(max_length=255, verbose_name="Operator Name")
    code = models.CharField(max_length=255, verbose_name="Operator Code")

    class Meta:
        unique_together = ("name", "code")

    def __str__(self):
        return f"{self.id}) {self.name}-{self.code}"

    def to_operator_schema(self) -> OperatorSchema:
        return OperatorSchema(
            name=self.name,
            code=self.code,
        )


class Client(models.Model):
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        validators=[
            validate_phone,
        ],
    )
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE, null=True)
    time_zone = models.CharField(
        max_length=32, choices=TIMEZONES_CHOICES, default=DEFAULT_TIMEZONE
    )

    tags = GenericRelation(ItemTag)

    class Meta:
        unique_together = ("phone_number", "operator", "time_zone")

    def __str__(self):
        return f"#{self.id} {self.operator} {self.phone_number}"

    def to_mailing_client(self) -> UserChemas.MailingUser:
        return UserChemas.MailingUser(
            id=self.id,
            operator=self.operator.to_operator_schema(),
            phone_number=int(self.phone_number),
            time_zone=self.time_zone,
        )


class ClientFilter(models.Model):
    tags = models.ManyToManyField(Tag)
    operators = models.ManyToManyField(Operator)

    def __str__(self):
        return f"Filter {self.id}"


class Mailing(models.Model):
    start_time = models.DateTimeField(verbose_name="Mailing starts")
    text = models.TextField(verbose_name="Mailing message")
    end_time = models.DateTimeField(verbose_name="Mailing finishes")
    client_filter = models.ForeignKey(
        ClientFilter, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = ("text", "client_filter", "end_time")

    def __str__(self):
        return f"{self.text[:50]}"

    def to_mailing_schema(self) -> MailingSchemas.MailingSchema:
        return MailingSchemas.MailingSchema(
            id=self.id,
            text=self.text,
            start_time=self.start_time,
            end_time=self.end_time,
        )


class Message(models.Model):
    class SendingStatus(models.TextChoices):
        NOT_SENT = "N", _("Not Sent")
        SENT = "S", _("Sent")

    status = models.TextField(
        verbose_name="Sending status",
        choices=SendingStatus.choices,
        default=SendingStatus.NOT_SENT,
    )
    created_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Message created at", auto_now_add=True
    )
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("mailing", "client", "status")

    def __str__(self):
        return f"Mailing {self.mailing.id} to {self.client}"

    def set_status_sent(self):
        self.status = self.SendingStatus.SENT

    def to_message_request(self) -> MessageSchemas.MessageRequestFull:
        return MessageSchemas.MessageRequestFull(
            id=self.id,
            phone=int(self.client.phone_number),
            mailing=self.mailing.to_mailing_schema(),
            client=self.client.to_mailing_client(),
            status=self.status,
        )


def update_message_status(message_id: int) -> bool:
    try:
        message_db = Message.objects.get(id=message_id)
        message_db.set_status_sent()
        message_db.save()
        return True
    except Exception:
        return False
