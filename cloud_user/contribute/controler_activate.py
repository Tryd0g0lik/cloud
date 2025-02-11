"""
cloud_user/contribute/controler_activate.py
This a function for control an authentication (from registrasion). \
This is, when, the user \
makes registration on the site.\
The 'send_activation_notificcation' from 'app.py' makes sending \
the email-message \
to the user email. \
Email contains the tokken-link. When user presses by the token-link, this run \
the function (below).


"""
import logging
import os
from datetime import datetime, timedelta
from django.core.signing import BadSignature
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from cloud_user.contribute.sessions import create_signer
from cloud_user.contribute.utilites import signer
from cloud_user.models import UserRegister
from rest_framework import status
from dotenv_ import (
    URL_REDIRECT_IF_NOTGET_AUTHENTICATION,
    URL_REDIRECT_IF_GET_AUTHENTICATION
)
import scrypt
from logs import configure_logging
from project.settings import (SESSION_COOKIE_HTTPONLY, SESSION_COOKIE_SECURE,
                              SESSION_COOKIE_SAMESITE, SESSION_COOKIE_AGE,
                              SECRET_KEY)
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
variable `user_session_{id}` and 'is_staff__{id}'. It is more info in README::COOKIE.
1. The user is registered on the site.\
2. The function is `send_activation_notification` from` app.py` sends an email with a tkene link to the user email address.\
3. The user presses on a token link.\
4. The function is `user_activate`.\
5. The function `user_activate` processes the URL requests \
containing a signature.\
6. The function accepts two parameters: `request` and` sign`. The `sign` \
parameter is a signature from the URL` Activate/<Str: Sign> `.\
7. The function is trying to decipher the signature and get the user name.\
8. If the decoding is successful, the function receives the user's object from\
 the database.\
9. If the user is already activated, the function returns a redirection with \
code 301.\
10. Otherwise, the function activates the user, sets the appropriate values
 in the user object and creates a user session.\
11. The function sets cuckoos for the user session and redirects the user to\
 the activation page.\
12. If an error occurs, the function returns redirecting with a code of 400.\
    :param request:\
    :param sign: str. It is 'sign' of signer from the url 'activate/<str:sign>'\
    :return:
    """
    _text = f"[{user_activate.__name__}]:"
    username = None
    try:
        log.info(f"{_text} START")
        sign = str(sign).replace("_null_", ":")
        username = signer.unsign(sign)
        log.info(f"{_text} Get '_first_name': {username.__str__()} ")
    except BadSignature as e:
        _text = f"{_text} Mistake => 'BadSignature': {e.__str__()}"
        # return redirect("/", permanent=True,)
        # https://docs.djangoproject.com/en/5.1/ref/request-response/#httpresponse-objects
        
        return HttpResponseRedirect(redirect_to=f"{URL_REDIRECT_IF_NOTGET_AUTHENTICATION}",
                                    status=status.HTTP_400_BAD_REQUEST)
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
            response = HttpResponseRedirect(redirect_to=f"{URL_REDIRECT_IF_NOTGET_AUTHENTICATION}",
                                            status=status.HTTP_400_BAD_REQUEST)
            return response
        _text = f"{_text} the object 'user' can not have 'True' value \
from 'is_activated'."
        log.info(_text)
        # get the text from the basis value
        _text = (_text.split(":"))[0] + ":"
        user.is_active = True
        user.is_activated = True
        user.is_staff = False
        user.last_login = datetime.utcnow()
        user.save()
        # /* --------------------- _text = f"{_text} the object 'user' can
        # not have 'True' value from 'is_activated'." --------------------- */
        # CREATE SIGNER
        user_session = create_signer(user)
        cache.set(f"user_session_{user.id}", user_session, SESSION_COOKIE_AGE)
        # cache.set(f"is_staff_{user.id}", user.is_staff, SESSION_COOKIE_AGE) # ????????????????????
        """ New object has tha `user_session_{id}` variable"""
        redirect_url = f"{request.scheme}://{request.get_host()}" \
f"{URL_REDIRECT_IF_GET_AUTHENTICATION}"
        response =  HttpResponseRedirect(redirect_url)
        
        # response.set_cookie(f"user_session_{user.id}",
        #OlD of VERSIONS
        response.set_cookie(f"user_session",
                            cache.get(
                                f"user_session_{user.id}"
                            ),
                            #  scrypt.hash(cache.get(
                            #     f"user_session_{user.id}"
                            # ), SECRET_KEY).decode('ISO-8859-1'),
                            max_age=SESSION_COOKIE_AGE,
                            httponly=True,
                            secure=SESSION_COOKIE_SECURE,
                            samesite=SESSION_COOKIE_SAMESITE
                            )
        # response.set_cookie(f"is_staff_{user.id}",
        response.set_cookie(f"is_staff",
                            user.is_staff,
                            max_age=SESSION_COOKIE_AGE,
                            httponly=True,
                            secure=SESSION_COOKIE_SECURE,
                            samesite=SESSION_COOKIE_SAMESITE)
        response.set_cookie(f"is_active",user.is_active,
                            max_age=SESSION_COOKIE_AGE,
                            httponly=SESSION_COOKIE_HTTPONLY,
                            secure=SESSION_COOKIE_SECURE,
                            samesite=SESSION_COOKIE_SAMESITE)
        response.set_cookie(
            f"index", str(user.id),
            max_age=SESSION_COOKIE_AGE,
            httponly=False,
            secure=SESSION_COOKIE_SECURE,
            samesite=SESSION_COOKIE_SAMESITE
            )
        return response

    except Exception as e:
        _text = f"{_text} Mistake => {e.__str__()}"
        return  HttpResponseRedirect(
            redirect_url=f"{request.scheme}://{request.get_host()}",
            status=400)
    finally:
        if "Mistake" in _text:
            log.error(_text)
        else:
            _text = 'Ok'
            log.info(_text)
