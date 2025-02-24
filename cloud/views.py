import json
import asyncio
from asgiref.sync import sync_to_async, async_to_sync
from typing import (NewType, TypedDict, Dict)
from rest_framework import (status, generics)
from rest_framework.renderers import JSONRenderer
from adrf import viewsets
from rest_framework.decorators import action
from django.core.cache import cache
from django.contrib.auth import login
from django.http.response import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect, csrf_exempt

from cloud.cookies import Cookies
from cloud.serializers import AdminSerializer
from cloud.services import get_data_authenticate
from cloud_file.models import FileStorage
from cloud_file.serializers import FileStorageSerializer
from cloud_user.models import UserRegister
from cloud_user.serializers import UserSerializer
# from project.services import get_fields_response


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
    async def options(self, request, *args, **kwargs):
        pass
        response = super().options(request, *args, **kwargs)
        return response

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

    async def list(self, request, *args, **kwargs):
        """
        :param args: None
        :param kwargs: None
        :return: method return list of users and their files
        """
        pass
        user_list = []
        user_files = []
        try:
            # CHECK IF USER IS AUTHENTICATED
            if request.user.is_authenticated and request.user.is_staff:
                # GET ALL USERS
                data_users = await sync_to_async(list)(UserRegister.objects.all())
                serializer_data_users = self.get_serializer(
                    list(data_users), many=True, allow_empty=True)
                # GET LIST OF USERS FROM SERIALIZER
                data_users_list = await sync_to_async(lambda: serializer_data_users.data)()
                user_list.extend(data_users_list)
    #
                # GET ALL FILES
                data_files = await sync_to_async(list)(
                        FileStorage.objects.all())
                # SERIALIZER ALL FILES
                if len(data_files) > 0:
                    serializer_data_files = FileStorageSerializer(list(data_files), many=True, allow_empty=True)
                    # GET LIST OF FILES FROM SERIALIZER
                    data_files_list = await sync_to_async(lambda: serializer_data_files.data)()
                    user_files.extend(data_files_list)
                response = JsonResponse(
                    data={"users": list(user_list),
                          "files": list(user_files)}, status=status.HTTP_200_OK)
                return response
            
            else:
                # NOT LOGGED IN
                response = JsonResponse(
                    {"detail": ["User is not authenticated"]},
                    status=status.HTTP_403_FORBIDDEN
                )
                if hasattr(request.user, 'id') and \
                  getattr(request.user, 'id') != None:
                    user = await sync_to_async(
                        UserRegister.objects.get)(pk=request.user.id)
                    user.is_active = False
                    user.save(update_fields=["is_active"])
                    login(request, user)
                elif hasattr(request.COOKIES, "index"):
                    user = await sync_to_async(UserRegister.objects.get)(
                        pk=int(getattr(request.COOKIES, "index"))
                    )
                    user.is_active = False
                    user.save(update_fields=["is_active"])
                    login(request, user)

                cookie = Cookies(request.user.id, response)
                response = cookie.is_active(False)
                return response

        except Exception as e:
            response = \
                JsonResponse({"detail":
                    f"[{__name__}::{self.__class__.__name__}.\
{self.list.__name__}]: Mistake => {e.__str__()}"},
                             status=status.HTTP_400_BAD_REQUEST)
            return response

    async def retrieve(self, request, *args, **kwargs):
        """
       :param args: None
       :param kwargs: None
       :return: method return data of one users and  his files
               """
        user_list = []
        user_files = []
        # response = super().retrieve(request, *args, **kwargs)
        try:
            # GET USER DATA AND FILES OF ONE USER
            if request.user.is_authenticated and request.user.is_staff:
                if "pk" in kwargs.keys():
                    # USER DATA
                    data_users = await sync_to_async(list)(
                        UserRegister.objects.filter(pk=int(kwargs["pk"]))
                    )
                    # FILES DATA
                    files_data = await sync_to_async(list)(
                        FileStorage.objects.filter(user_id=int(kwargs["pk"]))
                    )
                    # SERIALIZER
                    serializer_data_user = self.get_serializer(
                        list(data_users), many=True, allow_empty=True
                        )
                    # GET LIST OF USERS FROM SERIALIZER
                    data_users_list = await sync_to_async(
                        lambda: serializer_data_user.data
                        )()
                    user_list.extend(data_users_list)
            
                    if len(files_data) > 0:
                        serializer_data_files = FileStorageSerializer(
                            list(files_data), many=True, allow_empty=True
                            )
                        # GET LIST OF FILES FROM SERIALIZER
                        data_files_list = await sync_to_async(
                            lambda: serializer_data_files.data
                            )()
                        user_files.extend(data_files_list)
                    response = JsonResponse(
                        data={"users": list(user_list),
                              "files": list(user_files)}, status=status.HTTP_200_OK
                    )
                    return response
                else:
                    # NOT LOGGED IN
                    response = JsonResponse(
                        {"detail": ["User is not authenticated"]},
                        status=status.HTTP_403_FORBIDDEN
                    )
                    if hasattr(request.user, 'id') and \
                      getattr(request.user, 'id') != None:
                        user = await sync_to_async(
                            UserRegister.objects.get
                        )(pk=request.user.id)
                        user.is_active = False
                        user.save(update_fields=["is_active"])
                        login(request, user)
                    elif hasattr(request.COOKIES, "index"):
                        user = await sync_to_async(UserRegister.objects.get)(
                            pk=int(getattr(request.COOKIES, "index"))
                        )
                        user.is_active = False
                        user.save(update_fields=["is_active"])
                        login(request, user)
                    cookie = Cookies(request.user.id, response)
                    response = cookie.is_active(False)
                    return response
            else:
                # NOT LOGGED IN
                response = JsonResponse(
                    {"detail": ["User is not authenticated"]},
                    status=status.HTTP_403_FORBIDDEN
                )
                if hasattr(request.user, 'id') and \
                  getattr(request.user, 'id') != None:
                    user = await sync_to_async(
                        UserRegister.objects.get)(pk=request.user.id)
                    user.is_active = False
                    user.save(update_fields=["is_active"])
                    login(request, user)
                elif hasattr(request.COOKIES, "index"):
                    user = await sync_to_async(UserRegister.objects.get)(
                        pk=int(getattr(request.COOKIES, "index"))
                    )
                    user.is_active = False
                    user.save(update_fields=["is_active"])
                    login(request, user)

                cookie = Cookies(request.user.id, response)
                response = cookie.is_active(False)
                return response
        except Exception as e:
            response = \
                JsonResponse(
                    {"detail":
                         f"[{__name__}::{self.__class__.__name__}.\
{self.list.__name__}]: Mistake => {e.__str__()}"},
                    status=status.HTTP_400_BAD_REQUEST
                    )
            return response
        
    @action(detail=True, url_name="delete", methods=["PUT"])
    async def remove(self, request, *args, **kwargs):
        status_data = {}
        status_code = status.HTTP_204_NO_CONTENT
        # GET FILE'S ID FROM LIST
        files_id_list = json.loads(request.body)["users"]
        try:
            if request.user.is_authenticated:
                user_session_client = request.COOKIES.get("user_session")
                # GET use-session from the cache (our
                # cacher table from settings.py)
                user_session_db = await sync_to_async(cache.get)(
                    f"user_session_{request.user.id}"
                )
                # USER IS NOT AUTHENTICATED
                if (user_session_db != user_session_client and not
                request.user.is_staff) or (
                  request.user.id != int(kwargs["pk"])
                  and not request.user.is_staff):
                    response = JsonResponse(
                        {"data": ["User is not authenticated"]},
                        status=status.HTTP_403_FORBIDDEN
                    )
                    user = await sync_to_async(UserRegister.objects.get)(
                        pk=request.user.id
                    )
                    # DEACTIVATION
                    user.is_active = False
                    user.save(update_fields=["is_active"])
                    login(request, user)
                    cookie = Cookies(request.user.id, response)
                    response = cookie.is_active(False)
                    return response
                # GET USER's'S LIST BY USER's ID FROM DB
                user_list = [await asyncio.create_task(
                    sync_to_async(list)(UserRegister.objects.filter(id=index))
                ) for index in files_id_list]
                user_list = [arr[0] for arr in user_list]
                if len(user_list) == 0:
                    return sync_to_async(JsonResponse)(
                        {"error": "'pk' invalid"},
                        status=status.HTTP_400_BAD_REQUEST
                        )
                # CREATE TASK OF ASYNC
                tasks = []
                for user in user_list:
                    # tasks.append(
                    #     sync_to_async(default_storage.delete)(
                    #         f"{user.file_path}"
                    #         )
                    # )
                    tasks.append(sync_to_async(user.delete)())
                # RUN THE DELETE USERS (ALL TASKS)
                await asyncio.gather(*tasks)
                status_code = status.HTTP_204_NO_CONTENT
            else:
                # NOT LOGGED IN
                status_data = {"detail": "User is not authenticated"}
                status_code = status.HTTP_401_UNAUTHORIZED
        except Exception as e:
            status_data = {"error": f"Mistake => {e.__str__()}"}
            status_code = status.HTTP_404_NOT_FOUND
        finally:
            return JsonResponse(status_data, status=status_code)
