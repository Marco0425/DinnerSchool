# Import nativas
import re
import requests

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

def getChoiceLabel(choices, value):
    for val, label in choices:
        if val == value:
            return label
    return None  # Si no lo encuentra

def getChoiceValue(choices, value):
    for val, lbl in choices:
        if lbl == value:
            return val
    return None  # Si no lo encuentra

def normalizar_email(raw):
    """
    Limpia un correo capturado por el usuario: quita espacios (incluso
    intermedios, ej. "juan. villegas@...") y pasa todo a minúsculas.
    Devuelve None si el resultado no es un correo válido.
    """
    limpio = re.sub(r'\s+', '', raw or '').lower()
    try:
        validate_email(limpio)
    except ValidationError:
        return None
    return limpio

def requestReCAPTCHA(recaptcha_response):
    data = {
        'secret': settings.RCSECRET_KEY,
        'response': recaptcha_response
    }
    r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
    return r.json()