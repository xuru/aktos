import contextlib
import json

from django.conf import settings
from django.db import models
from rest_framework.fields import JSONField

from aktos.common.encryption import AESCipher


class EncryptedFieldMixin:
    def __init__(self, *args, **kwargs):
        self.cipher = AESCipher(settings.SECRET_KEY[:32])
        self.encrypt_only = kwargs.pop("encrypt_only", False)
        super().__init__(*args, **kwargs)

    def get_internal_type(self):
        return "TextField"

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def to_python(self, value):
        if value is None:
            return value

        if not self.encrypt_only:
            value = self.decrypt_value(value)
        return super().to_python(value)

    def decrypt_value(self, value):
        with contextlib.suppress(Exception):
            value = self.cipher.decrypt(value)
        return value

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if value is None:
            return value
        if not isinstance(value, str):
            value = str(value)
        return self.cipher.encrypt(value)

    def get_db_prep_value(self, value, connection, prepared=False):
        if not prepared:
            value = self.get_prep_value(value)
        return value

    @classmethod
    def values_match(cls, encrypted_value, raw_value):
        decrypted_value = cls().decrypt_value(encrypted_value)
        return decrypted_value is not None and len(decrypted_value) > 0 and decrypted_value == raw_value


class EncryptedTextField(EncryptedFieldMixin, models.TextField):
    pass


class EncryptedCharField(EncryptedFieldMixin, models.CharField):
    pass


class EncryptedDateField(EncryptedFieldMixin, models.DateField):
    def to_python(self, value):
        if value is None:
            return value

        if not self.encrypt_only:
            value = self.decrypt_value(value)

        return super().to_python(value)


class EncryptedJsonField(EncryptedFieldMixin, JSONField):
    def db_type(self, connection):
        return "text"

    def to_python(self, value):
        if value is None:
            return value

        if not self.encrypt_only:
            with contextlib.suppress(Exception):
                value = self.cipher.decrypt(value)

        # DJango/Postgres adds a single quote to the start/end of the blob - remove it and cast to json
        if isinstance(value, str) and len(value) > 1 and value.startswith("'") and value.endswith("'"):
            value = value[1:-1]

        with contextlib.suppress(BaseException):
            value = json.loads(value)

        return super(JSONField, self).to_python(value)
