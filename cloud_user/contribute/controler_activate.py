"""
cloud_user/contribute/controler_activate.py
This a function for control an authentication. This is, when, the user \
makes registration on the site.\
The 'send_activation_notificcation' from 'app.py' makes sending the email-message \
to the user email. \
Email contains the tokken-link. When user presses by the token-link, this run \
the function (below).
"""
import logging
from django.core.signing import BadSignature
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from cloud_user.contribute.sessions import create_signer
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
    """
    TODO: From the *_user/serializers.py::UserSerializer.create the message \
(contain referral link) go out to the user's email.\
\
Function changes the 'sign' of signer from the url 'activate/<str:sign>'.\
If all is OK,  we get the 301 code by \
the var 'URL_REDIRECT_IF_GET_AUTHENTICATION'. Plus, variables:
- user.is_active = True
- user.is_activated = True (of table 'UserRegister').
\
Response (of HttpResponseRedirect)  has data for the cookie. Data of \
variable `user_session_{id}` and 'is_superuser__{id}'. It is more info in README::COOKIE.
    :param request:
    :param sign: str. It is 'sign' of signer from the url 'activate/<str:sign>'
    :return:
    """
    _text = f"[{user_activate.__name__}]:"
    username = None
    try:
        log.info(f"{_text} START")
        username = signer.unsign(sign)
        log.info(f"{_text} Get '_first_name': {username.__str__()} ")
    except BadSignature as e:
        _text = f"{_text} Mistake => 'BadSignature': {e.__str__()}"
        # return redirect("/", permanent=True,)
        # https://docs.djangoproject.com/en/5.1/ref/request-response/#httpresponse-objects
        HttpResponseRedirect.__init__( # !!!! Проверка - работает или нет
            status=404,
        )
        return HttpResponseRedirect(f"{URL_REDIRECT_IF_NOTGET_AUTHENTICATION}")
    # https://docs.djangoproject.com/en/5.1/topics/http/shortcuts/#get-object-or-404
    try:
        user = get_object_or_404(UserRegister, username=username)
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
            response = HttpResponseRedirect(f"{URL_REDIRECT_IF_NOTGET_AUTHENTICATION}")
            return response
        _text = f"{_text} the object 'user' can not have 'True' value \
from 'is_activated'."
        log.info(_text)
        # get the text from the basis value
        _text = (_text.split(":"))[0] + ":"
        user.is_active = True
        user.is_activated = True
        user.save()
        # /* --------------------- _text = f"{_text} the object 'user' can
        # not have 'True' value from 'is_activated'." --------------------- */
        # CREATE SIGNER
        user_session = create_signer(user)
        cache.set(f"user_session_{user.id}", user_session, 86400)
        cache.set(f"is_superuser_{user.id}", user.is_superuser, 86400)
        """ New object has tha `user_session_{id}` variable"""
        data = {}
        # SESSION KEY unique for user identification
        data[f"user_session_{user.id}"] = cache.get(f"user_session_{user.id}")
        # COOCLIE SUPERUSER
        data[f'is_superuser_{user.id}'] = cache.get(f"is_superuser_{user.id}")
        return HttpResponseRedirect(URL_REDIRECT_IF_GET_AUTHENTICATION, {**data})
    except Exception as e:
        _text = f"{_text} Mistake => {e.__str__()}"
    finally:
        if "Mistake" in _text:
            log.error(_text)
        else:
            _text = 'Ok'
            log.info(_text)
