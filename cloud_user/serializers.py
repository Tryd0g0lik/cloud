"""Here is a serializer fot user registration"""
import logging
from rest_framework import serializers

from cloud_user.apps import signal_user_registered
from cloud_user.models import UserRegister
from logs import configure_logging, Logger

configure_logging(logging.INFO)
log = logging.getLogger(__name__)

class RegisterUserSerializer(serializers.ModelSerializer, Logger):
    log.info("START")
    class Meta:
        model = UserRegister
        fields = ["id", "is_superuser", "first_name", "last_name",
                  "last_login", "email", "is_active", ]
        log.info("Meta was!")

    def create(self, validated_data):
        _text = f"[{self.print_class_name()}.\
{self.create.__name__}]:"
        user = None
        try:
            _user = UserRegister.objects.create(**validated_data)
            if not _user:
                _text = f"{_text} Something what wrong!"
                raise ValueError()
            
            log.info(_text)
            # Create the new user
            _user.send_messages = True
            _user.is_active = False
            _user.activated = False
            _user.is_superuser = False
            _user.save()
            _text = f"{_text} Saved the new user."
            log.info(_text)
            # get the text from the basis value
            _text = (_text.split(":"))[0] + ":"
            # Send of Signal
            # https://docs.djangoproject.com/en/4.2/topics/signals/#sending-signals
            signal_user_registered.send_robust(RegisterUserSerializer,
                                        isinstance=_user)
            _text = f"{_text} Signal was sent."
            return _user
        except Exception as e:
            _text = f"{_text} Mistake => {e.__str__()}"
        finally:
            if "Mistake" in _text:
                log.error(_text)
            else:
                log.info(_text)
        
        # def update(self, instance, validated_data):
        #     pass
            