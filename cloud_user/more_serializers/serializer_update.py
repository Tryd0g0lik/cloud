"""
cloud_user/more_serializers/serializer_update.py
"""
import logging
from rest_framework import serializers
from cloud_user.models import UserRegister
from cloud_user.contribute.services import get_fields_response
from logs import configure_logging, Logger

configure_logging(logging.INFO)
log = logging.getLogger(__name__)

class UserPatchSerializer(serializers.ModelSerializer):
    """
    return \
         ```json
           {
             "id": 19,
             "last_login": null,
             "is_superuser": false,
             "username": "",
             "first_name": "Денис",
             "last_name": "Королев",
             "is_staff": false,
             "is_active": true,
             "date_joined": "2025-01-03T13:01:53.238635+07:00"
           }
   """
    class Meta:
        model = UserRegister
        fields = "__all__"
    
    
    
    def update(self, instance, validated_data: [list, dict]) -> object:
        ## Отработать с cookie
        """
        TODO: This for a PATCH method. For update data of single cell or more cells.
            Method: PATCH
            URL: for a contact is "api/v1/users/patch/<int:pk>"
            Method: PUT is not works.
        :param validated_data: [list, dict].\
            For change the single cell
            ```json // it for the logout
                {
                    "is_active": False // user is logout
                }
            ```
            or more
            ```json // it for the login
                { // user  when run the activate event
                    "email": < user@email.this >
                    "password": < user_password >
                    "token": < string >
                }
            ```
           
        :return instance: object \
        ```json
            {
              "id": 20,
              "last_login": null,
              "is_superuser": false,
              "username": "Rabbit",
              "first_name": "Денис",
              "last_name": "Сергеевич",
              "is_staff": false,
              "is_active": false,
              "date_joined": "2025-01-08T16:47:53.883666+07:00"
            }
        '''
        """
        
        
        # instance = super().update(instance, validated_data)
        instance = get_fields_response(self)
        
        return instance
    
    
    