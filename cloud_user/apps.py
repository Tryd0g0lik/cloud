"""Here is register app the "cloud_user and receiver function \
the 'user_registered_dispatcher' in 'Signal'. It is by activation \
the total app.
"""

import logging
from django.apps import AppConfig
from django.dispatch import Signal

from cloud_user.contribute.utilites import send_activation_notificcation
from logs import configure_logging

configure_logging(logging.INFO)
log = logging.getLogger(__name__)
log.info("START")

class CloudUserConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cloud_user"
    verbose_name = "Профиль пользователя"
    
    
    
# send message from the registration part
# https://docs.djangoproject.com/en/4.2/topics/signals/#defining-signals
# Look down
signal_user_registered = Signal(use_caching=False)
log.info(f"{__name__} Signal WAS STARTED")

def user_registered_dispatcher(sender, **kwargs)-> bool:
    """
    TODO: Send an activation message by the user email.\
        This is interface from part of registration the new user.\
        Message, it contains the signature of link for authentication
        /
        All interface by the user's authentication in folder '**/contribute'  and \
        look up the  'signal_user_registered.send(....)' code, and
        by module the 'cloud_user', plus the function 'user_activate' by \
        module the 'cloud_user'.
    :param sender:
    :param kwargs:
    :return: bool
    """
    __text = f"[{user_registered_dispatcher.__name__}]: "
    log.info(f"{__text} START")
    _resp_bool = False
    try:
        send_activation_notificcation(kwargs["instance"])
        _resp_bool = True
        __text = f"{__text} The activation message was added"
    except Exception as e:
        __text = f"{__text} Mistake => {e.__str__()}"
        _resp_bool = True
    finally:
        if "Mistake" in f"{__text}":
            log.error(__text)
        else:
            log.info(__text)
        __text = f"{__text} END"
        log.info(__text)
        return _resp_bool

log.info(f" The 'user_registered' is before the beginning")
signal_user_registered.connect(weak=False,
                               receiver=user_registered_dispatcher)
# After connect
# https://docs.djangoproject.com/en/4.2/topics/signals/#sending-signals
# Find the line where, it has sub-string 'signal_user_registered.send(....)'
