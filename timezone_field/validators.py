from django.core.validators import MaxLengthValidator

class TzMaxLengthValidator(MaxLengthValidator):
    clean = lambda self, x: len(unicode(x))
