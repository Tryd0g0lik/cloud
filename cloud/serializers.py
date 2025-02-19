from base64 import b64encode
from asgiref.sync import sync_to_async
from django.http import JsonResponse
from rest_framework import (serializers, status)
from scrypt import scrypt
from project.settings import SECRET_KEY
from cloud_user.models import UserRegister

class AdminSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = UserRegister
        fields = "__all__"
        # read_only_fields = ('id', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'date_joined')
        # extra_kwargs = {'password': {'write_only': True}}
    
    async def create(self, validated_data):
        pass
        try:
            from cloud_user.apps import signal_user_registered
            _user = await sync_to_async(UserRegister.objects.create)(**validated_data)
            if not _user:
                return JsonResponse({"detail": "User not created (serisalizer)"},
                                    status=status.HTTP_400_BAD_REQUEST)
            # CHANGE USER's PROPERTIES
            _user.send_messages = True
            _user.is_active = False
            _user.is_activated = False
            _user.is_staff = True
            
            # HASH PASSWORD
            b_password = scrypt.hash(
                f"pbkdf2${str(20000)}${(lambda: validated_data['password'])()}",
                SECRET_KEY
            )
            _user.password = b64encode(b_password).decode()
            # SAVE USER's PROPERTIES
            await sync_to_async(_user.save)()
            # SEND OF SIGNAL. Sends the message with the referral link to \
            # the user's email.
            await sync_to_async(signal_user_registered.send_robust)(AdminSerializer,
                                               isinstance=_user)
            return _user
        except Exception as err:
            return JsonResponse(
                {"detail": f"[{__name__}::{self.__class__.__name__}.\
{self.create.__name__}]: User not created (serisalizer). \
Mistake => {err.__str__()}"}, status=status.HTTP_400_BAD_REQUEST)
    async def update(self, instance, validated_data):
        pass
        response = super().update(instance, validated_data)
        return response