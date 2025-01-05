import logging
from rest_framework import serializers
from cloud_user.models import UserRegister
from logs import configure_logging, Logger

configure_logging(logging.INFO)
log = logging.getLogger(__name__)


# class UpdateUserSerializer(serializers.ModelSerializer):
#     """
#     username password first_name last_name last_login email
#      is_staff is_active date_joined is_superuser groups
#      user_permissions is_activated is_staff send_messages
#      data_joined
#
#     """
#     class Meta:
#         model = UserRegister
#         fields = ["id", "is_superuser", "first_name", "last_name",
#                   "last_login", "email", "is_active", ]
# #
#     def create(self, validated_data):
#         pass

class LoginUpSerializer(serializers.ModelSerializer):
    """
    username password first_name last_name last_login email
     is_staff is_active date_joined is_superuser groups
     user_permissions is_activated is_staff send_messages
     data_joined

    """

    class Meta:
        model = UserRegister
        fields = ["id", "is_active",]
    
   
        
    # def create(self, validated_data):
    #     pass