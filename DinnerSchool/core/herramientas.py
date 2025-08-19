# Import nativas
import requests

from django.conf import settings

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

def requestReCAPTCHA(recaptcha_response):
    data = {
        'secret': settings.RCSECRET_KEY,
        'response': recaptcha_response
    }
    r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
    return r.json()