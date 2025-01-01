"""Here is a serializer fot user registration"""
import logging
from rest_framework import serializers
from cloud_user.models import UserRegister
from logs import configure_logging, Logger

configure_logging(logging.INFO)
log = logging.getLogger(__name__)

class RegisterUserSerializer(serializers.ModelSerializer, Logger):
    log.info("START")
    class Meta:
        model = UserRegister
        fields = ["id", "first_name","last_name",
                  "last_login", "email", "password"]
        log.info("Meta was!")
