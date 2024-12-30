from django.apps import AppConfig
from django.dispatch import Signal

from cloud_user.contribute.utilites import send_activation_notificcation



class CloudUserConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cloud_user"
    verbose_name = "Профиль пользователя"
    
# send message from the registration part
user_registerred = Signal(use_caching=False)
def user_registered_dispatcher(sender, **kwargs):
    send_activation_notificcation(kwargs["instance"])

user_registerred.connect(weak=False,
                         receiver=user_registered_dispatcher)
