"""
cloud_user/contribute/utilites.py
"""
import logging
import scrypt
from django.core.signing import Signer
from django.template.loader import render_to_string

from dotenv_ import (APP_SERVER_HOST,
                     APP_PROTOKOL, APP_PORT)
from logs import configure_logging
configure_logging(logging.INFO)
log = logging.getLogger(__name__)


log.info("START")
# Integer signature
signer = Signer()
log.info("Received a signature")

def send_activation_notificcation(user) -> bool:
    """
    TODO: This function send (after the Signal) a message by email from user.\
     This is the part \
     authentication of the user.
     Note: Look up the 'user_registered_dispatcher' from 'apps.py'
    :param user: object
    """
    from project.settings import ALLOWED_HOSTS
    _host: [str, None] = None
    _resp_bool = False
    __text = f"[{send_activation_notificcation.__name__}]: "
    try:
        log.info(f"{__text} Before getting the 'ALLOWED_HOSTS'")
        if ALLOWED_HOSTS:
            url = f"{APP_PROTOKOL}://{ALLOWED_HOSTS[0]}"
            url_list = [ view_url.replace(
                f"{ALLOWED_HOSTS[0]}",
                f"{ALLOWED_HOSTS[0]}:{APP_PORT}")
                         if APP_PROTOKOL else view_url
                         for view_url in [url]]
            _host = url_list[0]
        else:
            log.info(f"{__text} The 'ALLOWED_HOSTS' not have.")
            url = f"{APP_PROTOKOL}://{APP_SERVER_HOST}"
            log.info(f"{__text} The 'APP_SERVER_HOST' was received.")
            url_list = [view_url.replace(
                f"{APP_SERVER_HOST}",
                f"{APP_SERVER_HOST}:{APP_PROTOKOL}")
                        if APP_PROTOKOL else view_url
                        for view_url in [url]]
            _host = url_list[0]
            
        _context: dict = {
            "user": user,
            "host": _host,
             "sign": signer.sign(user.username).replace(":", "_null_")}
        # LETTER 1
        log.info(f"{__text} Create a template for admin")
        subject = render_to_string(
            template_name='email/activation_letter_subject.txt',
            context=_context
            )
        log.info(f"{__text} Create a template for letter the number one ")
        # LETTER 2
        file_name = 'email/activation_letter_body.txt'
        if user.is_superuser:
            file_name = 'email/activation_admin_letter_body.txt'
        body_text = render_to_string(
            template_name=file_name,
            context=_context
        )
        log.info(f"{__text} Create a template for letter the number two ")
        # RUN THE 'email_user' METHOD FROM BASIS THE uSER MODEL
        # https://docs.djangoproject.com/en/5.1/topics/email/
        user.email_user(subject, body_text) # "work80@mail.ru", ["work80@mail.ru"],  fail_silently=False,
        _resp_bool = True
        __text = f"{__text} Message send by email of the user."
    except Exception as e:
        __text = f"{__text} Mistake => {e.__str__()}"
    finally:
        if "Mistake" in f"{__text}":
            log.error(__text)
            return False
        else:
            log.info(__text)
        __text = f"{__text} END"
        log.info(__text)
        return _resp_bool

