"""
This a function for control an authentication. This is, when, the user \
makes registration on the site.\
The 'send_activation_notificcation' from 'app.py' makes sending the email-message \
to the user email. \
Email contains the tokken-link. When user presses by the token-link, this run \
the function (below).
"""
import logging
from django.urls import reverse
from django.core.signing import BadSignature
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import (redirect, get_object_or_404)

from cloud_user.contribute.utilites import signer
from cloud_user.models import UserRegister
from dotenv_ import (
    URL_REDIRECT_IF_NOTGET_AUTHENTICATION,
    URL_REDIRECT_IF_GET_AUTHENTICATION
)
from logs import configure_logging

configure_logging(logging.INFO)
log = logging.getLogger(__name__)


"""Срабатывает по запросы урла который содержит подпись"""
def user_activate(request, sign):
    
    _text = f"[{user_activate.__name__}]:"
    _first_name = None
    try:
        log.info(f"{_text} START")
        _first_name = signer.unsign(sign)
        log.info(f"{_text} Get '_first_name': {_first_name.__str__()} ")
    except BadSignature as e:
        _text = f"{_text} Mistake => 'BadSignature': {e.__str__()}"
        # return redirect("/", permanent=True,)
        # https://docs.djangoproject.com/en/5.1/ref/request-response/#httpresponse-objects
        HttpResponseRedirect.__init__( # !!!! Проверка - работает или нет
            status=404,
        )
        return HttpResponseRedirect(f"{URL_REDIRECT_IF_NOTGET_AUTHENTICATION}/")
    # https://docs.djangoproject.com/en/5.1/topics/http/shortcuts/#get-object-or-404
    try:
        user = get_object_or_404(UserRegister, first_name=_first_name)
        try:
            _text = f"{_text} Get 'user': {user.__dict__.__str__()}"
            # logging, it if return error
        except Exception as e:
            _text = f"{_text} Get 'user': {user.__str__()}"
        log.info(_text)
        # get the text from the basis value
        _text = (_text.split(":"))[0] + ":"
        # check of activated
        if user.is_activated:
            _text = f"{_text} the object 'user' has 'True' value \
from 'is_activated'. Redirect. 301"
            # _http = HttpResponseRedirect.__init__(
            #     redirect_to='admin/')
            response = HttpResponseRedirect(f"{URL_REDIRECT_IF_NOTGET_AUTHENTICATION}/")
            # response = HttpResponseRedirect(URL_REDIRECT_IF_NOTGET_AUTHENTICATION)
            return response
        _text = f"{_text} the object 'user' can not have 'True' value \
from 'is_activated'."
        log.info(_text)
        # get the text from the basis value
        _text = (_text.split(":"))[0] + ":"
        user.is_active = True
        user.is_activated = True
        user.save()
        _text = f"{_text} the object 'user' can not have 'True' value \
from 'is_activated'."
        return HttpResponseRedirect(URL_REDIRECT_IF_GET_AUTHENTICATION)
    except Exception as e:
        _text = f"{_text} Mistake => {e.__str__()}"
    finally:
        if "Mistake" in _text:
            log.error(_text)
        else:
            log.info(_text)
