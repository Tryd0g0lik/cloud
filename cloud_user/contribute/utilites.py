import os
import logging
from django.core.signing import Signer
from django.template.loader import render_to_string
from project.settings import ALLOWED_HOSTS
from dotenv_ import (APP_SERVER_HOST,
                     APP_PROTOKOL)
from logs import configure_logging
configure_logging(logging.INFO)
log = logging.getLogger(__name__)

log.info(f"{__name__} START")
# Integer signature
signer = Signer()
log.info(f"{__name__} Received a signature")

def send_activation_notificcation(user) -> bool:
    """
    Send a message by email of the user. This is the part
    :param user: object
    """
    __host: [str, None] = None
    __resp_bool = False
    __text = f"[{send_activation_notificcation.__name__}]: "
    try:
        __text = f"{__text} Before getting the 'ALLOWED_HOSTS'"
        if ALLOWED_HOSTS:
            url = f"{APP_PROTOKOL}://{ALLOWED_HOSTS[0]}"
            url_list = [ view_url.replace(
                f"{ALLOWED_HOSTS[0]}",
                f"{ALLOWED_HOSTS[0]}:{APP_PROTOKOL}")
                         if APP_PROTOKOL else view_url
                         for view_url in [url]]
            __host = url_list[0]
        else:
            __text = f"{__text} The 'ALLOWED_HOSTS' not have."
            url = f"{APP_PROTOKOL}://{APP_SERVER_HOST}"
            __text = f"{__text} The 'APP_SERVER_HOST' was received."
            url_list = [view_url.replace(
                f"{APP_SERVER_HOST}",
                f"{APP_SERVER_HOST}:{APP_PROTOKOL}")
                        if APP_PROTOKOL else view_url
                        for view_url in [url]]
            __host = url_list[0]
            
        __context: dict = {
            "user": user,
            "host": __host,
            "sign": signer.sign(user.username)}
        subject = render_to_string(template_name= \
                                       'email/activation_letter_subject.txt',
                                   context=__context
                                   )
        __text = f"{__text} Before render to string."
        body_text = render_to_string(
            'email/activation_letter_body.txt',
            context=__context
        )
        __text = f"{__text} Message send by email of the user."
        user.email_user(subject, body_text)
        __resp_bool = True
    except Exception as e:
        __text = f"{__text} Mistake => {e.__str__()}"
    finally:
        log.info(__text)
        __text = f"{__text} END"
        return __resp_bool