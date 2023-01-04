from django.core.exceptions import ValidationError
import re


def validate_phone(value: str):
    pattern = r'''^(\+7|7)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$'''
    if not re.match(pattern, value):
        raise ValidationError(
            f'''{value} is not a valid phone number'''
        )
