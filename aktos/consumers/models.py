import decimal
import uuid

from django.db import models
from model_utils.fields import StatusField
from model_utils.models import TimeStampedModel

from aktos.common.encrypted_fields import EncryptedCharField
from aktos.consumers.enums import US_STATES
from aktos.consumers.enums import ConsumerStatus


class ConsumerAddress(TimeStampedModel):
    address1 = EncryptedCharField(max_length=2048)
    address2 = EncryptedCharField(max_length=2048, null=True, blank=True)
    city = EncryptedCharField(max_length=2048)
    state = EncryptedCharField(max_length=32, choices=US_STATES)
    zip_code = EncryptedCharField(max_length=32)


class Consumer(TimeStampedModel):
    STATUS = ConsumerStatus.choices

    address = models.OneToOneField(
        ConsumerAddress,
        on_delete=models.CASCADE,
        related_name="consumer",
        null=True,
        blank=True,
    )
    ref_id = models.UUIDField(default=uuid.uuid4)
    ssn = EncryptedCharField(max_length=2048)
    name = models.CharField(max_length=128)
    status = StatusField()
    balance = models.DecimalField(
        max_digits=18,
        decimal_places=10,
        default=decimal.Decimal("0.0"),
        help_text="The balance amount",
    )

    class Meta:
        unique_together = ("name", "ref_id")
