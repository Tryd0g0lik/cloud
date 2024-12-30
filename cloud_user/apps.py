import logging
from django.apps import AppConfig
from django.dispatch import Signal

from cloud_user.contribute.utilites import send_activation_notificcation
from logs import configure_logging
configure_logging(logging.INFO)
log = logging.getLogger(__name__)
log.info(f"{__name__} START")

class CloudUserConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cloud_user"
    verbose_name = "Профиль пользователя"
    
# send message from the registration part
user_registerred = Signal(use_caching=False)
log.info(f"{__name__} Signal WAS STARTED")
def user_registered_dispatcher(sender, **kwargs)-> bool:
    """
    TODO: Send an activation message by the user email.\
        This is interface from part of registration the new user.\
        Message, it contains the signature of link for authentication
    :param sender:
    :param kwargs:
    :return: bool
    """
    __text = f"[{user_registered_dispatcher.__name__}]: "
    log.info(f"{__text} START")
    __resp_bool = False
    try:
        send_activation_notificcation(kwargs["instance"])
        __resp_bool = True
        __text = f"{__text} The activation message was added"
    except Exception as e:
        __text = f"{__text} Mistake => {e.__str__()}"
        __resp_bool = True
    finally:
        if "Mistake" in f"{__text}":
            log.error(__text)
        else:
            log.info(__text)
        __text = f"{__text} END"
        log.info(__text)
        return __resp_bool
        
log.info(f"{__name__} the {user_registerred.__name__} is before the beginning")
user_registerred.connect(weak=False,
                         receiver=user_registered_dispatcher)
log.info(f"{__name__} END")
