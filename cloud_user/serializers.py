"""
cloud_user/serializers.py
Here is a serializer fot user registration
"""
import logging
import scrypt
from rest_framework import serializers
from cloud_user.apps import signal_user_registered
from cloud_user.models import UserRegister
from cloud_user.contribute.services import find_superuser
from logs import configure_logging, Logger
from project.settings import SECRET_KEY

configure_logging(logging.INFO)
log = logging.getLogger(__name__)


class UserSerializer(serializers.ModelSerializer, Logger):
    log.info("START")
    class Meta:
        model = UserRegister
        fields = "__all__"
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
            # Cot czn registrate the superuser of user
            _user.is_superuser = False
            _user.is_staff = False

            # /* -----------------временно HASH----------------- */
            _user.password = str(
                scrypt.hash(
                    f"pbkdf2${str(20000)}${(lambda: validated_data['password'])()}", SECRET_KEY
                    ).decode('windows-1251')
                )
            _user.save()
            _text = f"{_text} Saved the new user."
            log.info(_text)
            # get the text from the basis value
            _text = (_text.split(":"))[0] + ":"

            # Send of Signal. Sends the message with the referral link for
            # user authentication.
            # The *_user/controler_activate.py::user_activate make changes in db.
            # https://docs.djangoproject.com/en/4.2/topics/signals/#sending-signals
            signal_user_registered.send_robust(UserSerializer,
                                               isinstance=_user)
            _text = f"{_text} Signal was sent."
            # _user = get_fields_response(_user)
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

    def update(self, instance, validated_data):
        superuser = find_superuser()
        if superuser: # ????? What the logic?
            superuser_id = superuser.id
            instance = None
            if validated_data["id"] == superuser_id:
                instance = super().update(instance, validated_data)
            else:
                validated_data["is_superuser"] = False
                instance = super().update(instance, validated_data)
            return instance
        instance = super().update(instance, validated_data)
        return instance
