"""
This a function for control an authentication. This is, when, the user \
makes registration on the site.\
The 'send_activation_notificcation' from 'app.py' makes sending the email-message \
to the user email. \
Email contains the tokken-link. When user presses by the token-link, this run \
the function (below).
"""
import logging

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
log.info("START")

"""Срабатывает по запросы урла который содержит подпись"""
def user_activate(request, sign):
    try:
        __username = signer.unsigna(sign)
    except BadSignature:
        # return redirect("/", permanent=True,)
        # https://docs.djangoproject.com/en/5.1/ref/request-response/#httpresponse-objects
        return HttpResponseRedirect.__init__(
            status=404,
        )
    # https://docs.djangoproject.com/en/5.1/topics/http/shortcuts/#get-object-or-404
    try:
        user = get_object_or_404(UserRegister, username=__username)
        if user.is_activated:
            _http = HttpResponseRedirect(
                redirect_to=URL_REDIRECT_IF_NOTGET_AUTHENTICATION)
            # _http["Location"] = "/"
        user.is_active = True
        user.is_activated = True
        user.save()
        return redirect(URL_REDIRECT_IF_GET_AUTHENTICATION)
    except Exception as e:
        pass
    finally:
        pass