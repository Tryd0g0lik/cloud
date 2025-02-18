import json
from typing import (NewType, TypedDict, Dict)
from rest_framework import (viewsets)
from django.core.cache import cache
from django.http.response import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect, csrf_exempt

from cloud.serializers import AdminSerializer
from cloud.services import get_data_authenticate
from cloud_user.models import UserRegister


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
   
class AdminView(viewsets.ModelViewSet):
    queryset = UserRegister.objects.all()
    serializer_class = AdminSerializer
    # permission_classes = [
    #
    # ]