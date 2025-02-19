import json
import asyncio
from asgiref.sync import sync_to_async, async_to_sync
from typing import (NewType, TypedDict, Dict)
from rest_framework import (status, generics)
from adrf import viewsets
from rest_framework.decorators import action
from django.core.cache import cache
from django.http.response import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect, csrf_exempt

from cloud.serializers import AdminSerializer
from cloud.services import get_data_authenticate
from cloud_user.models import UserRegister
from cloud_user.serializers import UserSerializer
from project import decorators_CSRFToken
from project.services import get_fields_response


@csrf_exempt
def user_update_sessionTime(request):
    """
    TODO: Updates the time of the session
    Entrypoint: SessionData_Type = {
        "time": 1900 # Time of seconds.
    }
    header: <'X-CSRFToken': csrftoken>
    :param index: Id of user from user's db.
    :param time: integer. Seconds for update the live time from property the\
    'user_session_{id}' and 'is_staff_{id}'
    :return: boolean, True - all OK or all NOT OK if we get the False.
    """
    response = JsonResponse({"message": "Not OK"})
    if request.method != "PATCH":
        return response
    
    # Get new type
    class SessionData_Type(TypedDict):
        time: int
    try:
        # Get user's Id from COOKIE
        instance = get_data_authenticate(request)
        data: SessionData_Type = json.loads(request.body.decode())
        cache.touch(f"user_session_{instance.id}", data["time"] * 2)
        cache.touch(f"is_staff_{instance.id}", data["time"] * 2)
        return JsonResponse({"message": "OK"})
    except Exception as e:
        raise ValueError(f"[{__name__}::{user_update_sessionTime.__name__}]: \
Mistake => {e.__str__()}")
    finally:
        cache.close()
   
class AdminView(viewsets.ModelViewSet, generics.GenericAPIView):
    queryset = UserRegister.objects.all()
    serializer_class = AdminSerializer
    # permission_classes = [
    #
    # ]
    @decorators_CSRFToken(True)
    async def options(self, request, *args, **kwargs):
        pass
        response = super().options(request, *args, **kwargs)
        return response
    
    
    # @decorators_CSRFToken(False)
    async def create(self, request, *args, **kwargs):
        pass
        try:
            # CHECK IF USER IS NOT AUTHENTICATED
            if request.method == "POST" and not request.user.is_authenticated:
                data_request = json.loads(request.body)
                
                # SERIALIZER
                serializer = AdminSerializer(data={**data_request})
                data_saved = None
                if await sync_to_async(serializer.is_valid)():
                    # IF SERIALIZE DATA IS VALID
                    data_saved = await serializer.create(serializer.validated_data)
                    pass
                    # await serializer.save()
                    
                else:
                    # IF SERIALIZER"s DATA NOT VALID
                    return JsonResponse(serializer.errors,
                                        status=status.HTTP_400_BAD_REQUEST)
                pass
                if (data_saved):
                    exclude_instance = []
                    if len(exclude_instance) == 0:
                        exclude_instance = ["_state", "password", "is_activated",
                                            "email", "send_messages",
                                            "groups", "user_permissions"]
                    new_instance = {}
                    for k, v in dict(data_saved.__dict__).items():
                        if k in exclude_instance:
                            continue
                        new_instance[f"{k}"] = v
                    return await sync_to_async(JsonResponse)(data={**new_instance}, status=status.HTTP_200_OK)
            else:
                # IF USER IS AUTHENTICATED FRO REQUEST
                return JsonResponse({"detail": "Check the user from REQUEST"},
                                    status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            return JsonResponse({"detail": f"[{__name__}::{self.__class__.__name__}.{self.create.__name__}]: \
Mistake => {err.__str__()}"}, status=status.HTTP_400_BAD_REQUEST)

    @decorators_CSRFToken(True)
    async def update(self, request, *args, **kwargs):
        pass
        response = super().update(request, *args, **kwargs)
        return response

    @decorators_CSRFToken(True)
    async def destroy(self, request, *args, **kwargs):
        pass
        response = super().destroy(request, *args, **kwargs)
        return response

    @decorators_CSRFToken(True)
    async def list(self, request, *args, **kwargs):
        pass
        response = super().list(request, *args, **kwargs)
        return response

    @decorators_CSRFToken(True)
    async def retrieve(self, request, *args, **kwargs):
        pass
        response = super().retrieve(request, *args, **kwargs)
        return response
