import requests

import settings

recaptcha_verify_url = 'https://www.recaptcha.net/recaptcha/api/siteverify'


def verify(response):
    parameters = {
        'secret': settings.reCAPTCHA.serverKey,
        'response': response
    }
    r = requests.post(recaptcha_verify_url, parameters)
    g_response = r.json()
    return g_response['success']
