import requests
from werkzeug.exceptions import BadRequest
from functools import wraps
from flask import request
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


def required_args(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not 'g-recaptcha-response' in request.args:
            raise NoRecaptcha
        g_recaptcha_response = request.args['g-recaptcha-response']
        v = verify(g_recaptcha_response)
        print(v)
        if v:
            return func(*args, **kwargs)
        else:
            raise RecaptchaError
    return wrapper


def required_form(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not 'g-recaptcha-response' in request.form:
            raise NoRecaptcha
        g_recaptcha_response = request.form['g-recaptcha-response']
        v = verify(g_recaptcha_response)
        if v:
            return func(*args, **kwargs)
        else:
            raise RecaptchaError
    return wrapper


class NoRecaptcha(BadRequest):
    description = 'reCAPTCHA not found.'

class RecaptchaError(BadRequest):
    description = 'reCAPTCHA validation failed.'
