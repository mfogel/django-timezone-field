from django.core.validators import MaxLengthValidator

class TzMaxLengthValidator(MaxLengthValidator):
    "Validate a timezone's string representation does not exceed max_length"
    clean = lambda self, x: len(unicode(x))
