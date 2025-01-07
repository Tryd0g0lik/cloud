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
        fields = ["id", "is_active", "email", "password"]
    
   
        
    def update(self, instance, validated_data: [list, dict]) -> object:
        ## Отработать с cookie
        """
        TODO: This the method for update date from the user's \
            login (activation).\
            URL for a contact is "api/v1/users/login/<int:pk>"
            Method: PATCH
        :param validated_data: [list, dict].\
            ```json // it for the logout
                {
                    "is_active": False // user is logout
                }
            ```
            or
            ```json // it for the login
                { // user  when run the activate event
                    "email": < user@email.this >
                    "password": < user_password >
                    "token": < string >
                }
            ```
            "is_active" the True it is means, what user the activated.
        :return instance: object
        """
        if validated_data["is_active"] and  \
            len(validated_data) == 1:
            instance = super().update(instance, validated_data)
            return  instance
        if \
          len(validated_data) == 2 and \
          validated_data["email"] and \
          validated_data["password"] and \
          validated_data["email"] == instance.email and \
          validated_data["password"] == instance.password:
            validated_data["is_active"] = True
            del validated_data["password"]
            del validated_data["email"]
            instance = super().update(instance, validated_data)
            return instance
            
        
        return instance
    
    
    