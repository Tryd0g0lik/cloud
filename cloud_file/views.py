"""
cloud_file/views.py
Here, interface of file storage.
"""
import asyncio
import json
from typing import TypedDict
import os

from asgiref.sync import sync_to_async
from django.http import (HttpResponse, JsonResponse)
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from adrf import viewsets
from rest_framework.decorators import action
from django.core.cache import cache

from cloud.cookies import Cookies
from cloud.hashers import md5_chacker
from cloud.services import get_data_authenticate
from cloud_user.models import UserRegister

from .models import FileStorage
from .serializers import FileStorageSerializer
from django.core.files.storage import default_storage
from datetime import datetime


class FileStorageViewSet(viewsets.ViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    queryset = FileStorage.objects.all()
    serializer_class = FileStorageSerializer

    # 
    async def list(self, request, *args, **kwargs) -> JsonResponse:
        status_data: [dict, list] = []
        status_code = status.HTTP_200_OK
        files = []
        
        try:
            if request.user.is_authenticated:
                user_session_client = request.COOKIES.get("user_session")
                # GET use-session from the cache  (our
                # cacher table from settings.py)
                user_session_db = await sync_to_async(cache.get)(
                    f"user_session_{request.user.id}"
                )
                # CHECK THE KEY of USER_SESSION
                if user_session_db != user_session_client:
                    response = JsonResponse(
                        {"data": ["User is not authenticated"]},
                        status=status.HTTP_403_FORBIDDEN)
                    user = await sync_to_async(UserRegister.objects.get)(pk=request.user.id)
                    user.is_active = False
                    user.save(update_fields=["is_active"])
                    login(request, user)
                    cookie = Cookies(request.user.id, response)
                    response = cookie.is_active(False)
                    return response
                instance = await sync_to_async(get_data_authenticate)(request)
                
                # IF USER IS ADMIN - RETURN ALL FILES FROM ALL USERS
                if request.user.is_staff:
                    if hasattr(kwargs, "pk"):
                        files = await sync_to_async(list)(
                            FileStorage.objects.filter(user_id=getattr(kwargs, "pk"))
                        )
                        if len(files) == 0:
                            # SERIALIZER
                            serializer = self.serializer_class(
                                files, many=True
                                )
                            status_data = serializer.data
                            return JsonResponse(
                                status_data,
                                status=status_code
                            )
                    files.extend(await sync_to_async(list)(FileStorage.objects.all()))
                elif hasattr(request.COOKIES, "index"):
                    files.extend(await sync_to_async(list)(
                        FileStorage.objects \
                            .filter(user_id=int(
                            getattr(request.COOKIES, "index")
                        ))
                    ))
                elif hasattr(kwargs, "pk"):
                    # #
                    files = await sync_to_async(list)(
                        FileStorage.objects\
                            .filter(user_id=int(getattr(kwargs, "pk"))))
                else:
                    files = []
                # USER HAVE NOT FILES - RETURN EMPTY LIST
                if len(files) == 0:
                    status_data = {"data": []}
                    status_code=status.HTTP_200_OK
                    return JsonResponse(
                        status_data,
                        status=status_code
                        )
                # SERIALIZER
                serializer = self.serializer_class(files, many=True)
                status_data = serializer.data
                if "[" in str(serializer.data):
                    status_data = {"data": list(serializer.data)}
                return JsonResponse(
                    status_data,
                    status=status_code
                    )
            else:
                # NOT LOGGED IN
                status_data = {"detail": "User is not authenticated"}
                status_code = status.HTTP_401_UNAUTHORIZED
                return JsonResponse(
                    status_data,
                    status=status_code
                    )
        except Exception as e:
            # ERROR IN SCRIPT
            status_data = {"error": f"[{self.__class__.list.__name__}]: \
            Mistake => {e.__str__()}"}
            status_code = status.HTTP_400_BAD_REQUEST
            return JsonResponse(
                status_data,
                status=status_code
                )
        finally:
            pass
    
    # 
    async def retrieve(self, request, *args, **kwargs):
        """
        Method GET for receive a single position
        :param request:
        :param args:
        :param kwargs: dict. {'pk': 21}
        :return:
        """
        status_code = status.HTTP_200_OK
        files = []
        try:
            if request.user.is_authenticated:
                user_session_client = request.COOKIES.get("user_session")
                # GET use-session from the cache (our
                # cacher table from settings.py)
                user_session_db = await sync_to_async(cache.get)(
                    f"user_session_{request.user.id}")
                # CHECK THE SESSION KEY of USER_SESSION
                if user_session_db != user_session_client and not request.user.is_staff:
                    response = JsonResponse(
                        {"data": ["User is not authenticated"]},
                        status=status.HTTP_403_FORBIDDEN
                        )
                    user = await sync_to_async(UserRegister.objects.get)(
                        pk=request.user.id
                        )
                    user.is_active = False
                    user.save(update_fields=["is_active"])
                    login(request, user)
                    cookie = Cookies(request.user.id, response)
                    response = cookie.is_active(False)
                    return response
                # CHECK USER ID
                if request.user.id != int(kwargs["pk"]) \
                  and not request.user.is_staff:
                    return JsonResponse(
                        {"error": "There is no access"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                # CHECK THE USER's PERMISSIONS
                if request.user.is_staff:
                    if int(kwargs["pk"]):
                        # GET FILES FROM SINGLE USER
                        files.extend(
                            await sync_to_async(list)(
                                FileStorage.objects.filter(
                                    user_id=int(kwargs["pk"])
                                    )
                            )
                            )
                    else:
                        # GET FILES FROM ALL USERS
                        files.extend(await sync_to_async(list)(
                            FileStorage.objects.all())
                                     )
                elif not request.user.is_staff:
                    # GET FILES FROM SINGLE USER
                    files.extend(await sync_to_async(list)(
                        FileStorage.objects.filter(user_id=int(kwargs["pk"]))
                    ))
                
                status_data = {"files": []}
                # SERIALIZER
                if type(files) == list and len(files) == 1:
                    serializer = self.serializer_class(files[0])
                    status_data = {"files": [serializer.data]}
                elif type(files) == list and len(files) > 1:
                    serializer = self.serializer_class(files, many=True)
                    status_data = {"files": serializer.data}
                return JsonResponse(
                    status_data,
                    status=status_code
                )
            else:
                # NOT LOGGED IN
                status_data = {"detail": "User is not authenticated"}
                status_code = status.HTTP_401_UNAUTHORIZED
                return JsonResponse(
                    status_data,
                    status=status_code
                )
            
        except Exception as e:
            # ERROR IN SCRIPT
            status_data = {
                "error": f"[{self.__class__.retrieve.__name__}]: \
                       Mistake => {e.__str__()}"}
            status_code = status.HTTP_400_BAD_REQUEST
            return JsonResponse(
                status_data,
                status=status_code
                )

    
    async def create(self, request):
        cookie_data = await sync_to_async(get_data_authenticate)(request)
        user_ind = getattr(cookie_data, "id")
        # GET THE FILE'S DATA from FORM
        file_obj = request.FILES.get('file')
        if not file_obj:
            return JsonResponse({"error": "No file provided"},
                                status=status.HTTP_400_BAD_REQUEST)
        try:
            if request.user.is_authenticated:
                user_session_client = request.COOKIES.get('user_session')
                # GET use-session from the cache (our
                # cacher table from settings.py)
                user_session_db = await sync_to_async(cache.get)(
                    f"user_session_{request.user.id}"
                )
                user = await sync_to_async(UserRegister.objects.get)(
                    pk=request.user.id
                )
                # CHECK THE SESSION KEY of USER_SESSION
                if user_session_db != user_session_client:
                    response = JsonResponse(
                        {"data": ["User is not authenticated"]},
                        status=status.HTTP_403_FORBIDDEN
                    )
                    
                    user.is_active = False
                    await  sync_to_async(user.save)(update_fields=["is_active"])
                    login(request, user)
                    cookie = Cookies(request.user.id, response)
                    response = cookie.is_active(False)
                    return response
                # if request.user.is_staff:
                #     response = JsonResponse(
                #         {"data": ["You not allowed to created a file for this profile"]},
                #         status=status.HTTP_403_FORBIDDEN
                #     )
                #     return response
                """
                Conservation a one file in serverby by path \
                'card/<year>/<month>/<day>/< file name >'
                First, we need to check the duplication file.  For this, we save the file \
                by path 'card/...'.
                
                """
                time_path = f"card/{user_ind}/{datetime.now().year}/{datetime.now().month}/{datetime.now().day}"
                
                # THE DOCUMENT FILE is TEMPORARY SAVING
                await sync_to_async(default_storage.save)(f"{time_path}/{file_obj.name}", file_obj)
                # CHECK ON FILE'S DUPLICATION
                result_bool = await asyncio.create_task(
                    FileStorageViewSet
                    .compare_twoFiles(f"{time_path}/{file_obj.name}",
                                      int(user_ind),
                                      FileStorage)
                )
                # CREATE A LINE FOR FILE'S DB IF NOT DUPLICATION
                if not result_bool:
                    # DELETE THE TEMPORARY FILE (above)
                    await sync_to_async(default_storage.delete)(f"{time_path}/{file_obj.name}")
                    # RE-SAVE A FILE TO SERVER BY
                    # A PATH 'uploads/<year>/<month>/<day>/< file name >'
                    time_path = time_path.replace("card/", "uploads/")
                    file_path = await asyncio.create_task(
                        sync_to_async(default_storage.save)\
                            (f"{time_path}/{file_obj.name}", file_obj)
                    )
                    file_record = await sync_to_async(FileStorage.objects.create)(
                        user=user,
                        original_name=file_obj.name,
                        size=file_obj.size,
                        file_path="%s" % file_path,
                    )
                    # SERIALIZER
                    serializer = FileStorageSerializer(file_record)
                    return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    # FOUND THE FILE'S DUPLICATION
                    await sync_to_async(default_storage.delete)(f"{time_path}/{file_obj.name}")
                    # time_path = time_path.replace("card/", "uploads/")
                    # Get the old file by path 'uploads/<year>/<month>/<day>/< file name >'
                    # /* --------------- А если файл переименован?? --------------- */
                    file_old_list = \
                        await sync_to_async(list)(FileStorage.objects\
                                                  .filter(original_name=f"{file_obj.name}"))
                    if len(file_old_list) > 0:
                        serializer = self.serializer_class(file_old_list[0])
                        return JsonResponse(serializer.data,
                                        status=status.HTTP_208_ALREADY_REPORTED)
                    
            else:
                # NOT LOGGED IN
                status_data = {"detail": "User is not authenticated"}
                status_code = status.HTTP_401_UNAUTHORIZED
                return JsonResponse(
                    status_data,
                    status=status_code
                )
        except FileStorage.DoesNotExist as err:
            # If something what wrong
            return JsonResponse(
                {"detail": f"Mistake => {err.__str__()}"},
                status=status.HTTP_400_BAD_REQUEST
                )
        finally:
            cache.close()
    async def destroy(self, request, *args):
        return sync_to_async(JsonResponse)({"error": "The wrong, incorrect request"})
    
    
    @action(detail=True, url_name="delete", methods=["PUT"])
    async def remove(self, request, **kwargs):
        """
        TODO: This is for delete a single file's line from db. .
        :param request:
        :param pk: integer from single line of db, for changing
        :return:
        """
        status_data = {}
        status_code =status.HTTP_204_NO_CONTENT
        # GET FILE'S ID FROM LIST
        files_id_list = json.loads(request.body)["files"]
        try:
            if request.user.is_authenticated:
                user_session_client = request.COOKIES.get("user_session")
                # GET use-session from the cache (our
                # cacher table from settings.py)
                user_session_db = await sync_to_async(cache.get)(
                    f"user_session_{request.user.id}"
                )
                # CHECK THE SESSION KEY of USER_SESSION  AND ADMIN adn CHECK USER ID
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
                    user.is_active = False
                    user.save(update_fields=["is_active"])
                    login(request, user)
                    cookie = Cookies(request.user.id, response)
                    response = cookie.is_active(False)
                    return response
                # GET FILE'S LIST BY FILE's ID FROM DB
                file_list = [await asyncio.create_task(
                    sync_to_async(list)(FileStorage.objects.filter(id=index))
                ) for index in files_id_list]
                file_list = [file[0] for file in file_list]
                if len(file_list) == 0:
                    return sync_to_async(JsonResponse)({"error": "'pk' invalid"},
                                        status=status.HTTP_400_BAD_REQUEST)
                # CREATE TASK OF ASYNC
                tasks = []
                for file in file_list:
                    tasks.append(
                        sync_to_async(default_storage.delete)(f"{file.file_path}")
                        )
                    tasks.append(sync_to_async(file.delete)())
                # RUN THE DELETE OLD FILES (ALL TASKS)
                await asyncio.gather(*tasks)
                status_code=status.HTTP_204_NO_CONTENT
            else:
                # NOT LOGGED IN
                status_data = {"detail": "User is not authenticated"}
                status_code = status.HTTP_401_UNAUTHORIZED
        except Exception as e:
            status_data = {"error": f"Mistake => {e.__str__()}"}
            status_code = status.HTTP_404_NOT_FOUND
        finally:
            return JsonResponse(status_data, status=status_code)

    
    @action(detail=True, url_name="rename",
            methods=['post'])
    async def rename(self, request, **kwargs):
        """
        TODO: This is for rename a single file's line from db. .
        :param request:
        :param pk: integer from single line of db, for changing
        :return:
        """
        try:
            
            new_name = ""
            file_id = ""
            if hasattr(request, "data"):
                new_name = new_name.replace("", request.data.get('new_name'))
                file_id = file_id.replace("", request.data.get('fileId'))
            elif hasattr(request, "body"):
                new_name = json.loads(request.body).get('new_name')
                file_id = json.loads(request.body).get('fileId')
            if not new_name:
                return JsonResponse(
                    {"error": "New name is required."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
        
            if request.user.is_authenticated:
                user_session_client = request.COOKIES.get("user_session")
                # GET use-session from the cache (our
                # cacher table from settings.py)
                user_session_db = await sync_to_async(cache.get)(
                    f"user_session_{request.user.id}"
                )
                # CHECK THE SESSION KEY of USER_SESSION  AND ADMIN adn CHECK USER ID
                if (user_session_db != user_session_client and not
                request.user.is_staff) or(
                  request.user.id != int(kwargs["pk"])
                      and not request.user.is_staff):
                    response = JsonResponse(
                        {"data": ["User is not authenticated"]},
                        status=status.HTTP_403_FORBIDDEN
                    )
                    user = await sync_to_async(UserRegister.objects.get)(
                        pk=request.user.id
                    )
                    user.is_active = False
                    user.save(update_fields=["is_active"])
                    login(request, user)
                    cookie = Cookies(request.user.id, response)
                    response = cookie.is_active(False)
                    return response
                
                # GET THE FILE BY FILE ID FOR RENAMING
                file_record_list =\
                    await sync_to_async(list)(FileStorage.objects
                                              .filter(id=int(file_id)))
                # CHECK THE NEW NAME IF EXISTS
                file_name_duplication = await sync_to_async(list)(FileStorage.objects
                                              .filter(original_name=new_name))
                # FOUND OF DUPLICATION
                if len(file_name_duplication) != 0:
                    return JsonResponse(
                        {"detail": "The file with this name already exists."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                # NOT FOUND FILE FOR RENAMING
                if len(file_record_list) == 0 :
                    return JsonResponse(
                        {"error": "Check the 'pk"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # GET ORIGINAL NAME FROM FILE
                user_original_name_fromFile =\
                    await asyncio.create_task(
                        sync_to_async(lambda: file_record_list[0].original_name)()
                    )
                file_extencion = str(user_original_name_fromFile).split(".")[-1]
                
                # RENAME OF FILE
                new_file_path = (file_record_list[0].file_path.path).replace(
                              file_record_list[0].file_path.name.split("/")[-1],
                    new_name) # f"{new_name}.{file_extencion}"
                os.rename(file_record_list[0].file_path.path, new_file_path)
                
                # GET PATH FOR THE DB
                file_record_list[0].original_name = new_name #f"{new_name}.{file_extencion}"
                file_record_list[0].file_path.name = \
                    "uploads" + new_file_path.replace("\\", "/").replace(r"//", "/")\
                        .split("uploads")[-1]
                await sync_to_async(file_record_list[0].save)()
                
                return JsonResponse(self.serializer_class(file_record_list[0]).data)
            else:
                # NOT LOGGED IN
                status_data = {"detail": "User is not authenticated"}
                status_code = status.HTTP_401_UNAUTHORIZED
                return JsonResponse(
                    status_data,
                    status=status_code
                )
        except (FileStorage.DoesNotExist, Exception) as e:
            return JsonResponse(
                {"detail": f"Mistake => {e.__str__()}"},
                status=status.HTTP_404_NOT_FOUND
            )

    #
    @action(detail=True,
            url_name="comment", methods=['PATCH'])
    async def update_comment(self, request,  **kwargs):
        try:
            new_comment = ""
            file_id = ""
            # GET DATA FROM REQUEST
            if hasattr(request, "data"):
                new_comment = new_comment.replace("", request.data.get('comment'))
                file_id = file_id.replace("", request.data.get('fileId'))
            elif hasattr(request, "body"):
                new_comment = json.loads(request.body).get('comment')
                file_id = json.loads(request.body).get('fileId')
            # http://127.0.0.1:8000/api/v1/files/31/update_comment/
            
            if not file_id or not new_comment:
                return sync_to_async(JsonResponse)(
                    {"error": "User not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if request.user.is_authenticated:
                user_session_client = request.COOKIES.get("user_session")
                # GET use-session from the cache (our
                # cacher table from settings.py)
                user_session_db = await sync_to_async(cache.get)(
                    f"user_session_{request.user.id}"
                )
                # CHECK THE SESSION KEY of USER_SESSION  AND ADMIN adn CHECK USER ID
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
                    user.is_active = False
                    user.save(update_fields=["is_active"])
                    login(request, user)
                    cookie = Cookies(request.user.id, response)
                    response = cookie.is_active(False)
                    return response
                # GET FILE BY FILE ID FOR RENAMING
                file_record_list = \
                    await sync_to_async(list)(
                        FileStorage.objects
                        .filter(id=int(file_id))
                        )
                # file_record_list = \
                #     await sync_to_async(list)(FileStorage.objects.filter(user_id=kwargs["pk"]).filter(pk=int(file_id)))
                if len(file_record_list) == 0:
                    return sync_to_async(JsonResponse)(
                        {"detail": "Mistake => File not found."},
                        status=status.HTTP_404_NOT_FOUND
                    )
                    
                file_record_list[0].comment = new_comment
                await sync_to_async(file_record_list[0].save)(update_fields=["comment"])
                
                return await sync_to_async(JsonResponse)(self.serializer_class(file_record_list[0]).data)
            else:
                # NOT LOGGED IN
                status_data = {"detail": "Mistake => User is not authenticated"}
                status_code = status.HTTP_401_UNAUTHORIZED
                return JsonResponse(
                    status_data,
                    status=status_code
                )
        except FileStorage.DoesNotExist:
            return await sync_to_async(JsonResponse)(
                {"error": "File not found."}, status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, url_name="download",
            methods=['GET'])
    async def download(self, request, **wargs):
        try:
            # GET file  from db
            file_record_list = \
                await sync_to_async(list)(FileStorage.objects\
                                          .filter(special_link=wargs["pk"]))
                
            if len(file_record_list) == 0:
                # Get data of line from db
                # /* -----------  lambda  ----------- */
                return JsonResponse(
                    {"error": "Check the 'pk"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Update the 'last_downloaded' from line
            # file_record_list[0].last_downloaded = datetime.utcnow()
            file_record_list[0].last_downloaded =str(datetime.utcnow())
            await sync_to_async(file_record_list[0].save)()
            # DOWNLOAD file
            response = HttpResponse(
                default_storage.open(file_record_list[0].file_path.name),
                content_type='application/octet-stream'
            )
            response['Content-Disposition'] = \
                f'attachment; filename="{file_record_list[0].original_name}"'
        
            return response
        except Exception as e:
            return JsonResponse(
                {"error": f"Mistake => {e.__str__()}"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    
    @action(detail=True, url_name="referral_links",
            methods=['GET'])
    async def referral_links(self, request, **kwargs):
        try:
            # GET the user ID from COOKIE
            cookie_data = await sync_to_async(get_data_authenticate)(request)
            user_ind = getattr(cookie_data, "id")
            file_id = request.COOKIES.get("fileId")
            # file_id = getattr(cookie_data, "fileId")
            file_record_list = \
                await sync_to_async(list)(
                    FileStorage.objects.filter(pk=int(file_id))
                )
            if len(file_record_list) == 0 :
                # Get data of line from db
                # /* -----------  lambda  ----------- */
                return JsonResponse(
                    {"error": "Check the 'pk"},
                    status=status.HTTP_400_BAD_REQUEST
                )
           
            user_session_client = getattr(cookie_data, "user_session")
            # GET use-session from the cache (table from db session)
            user_session_db = await sync_to_async(cache.get)(
                f"user_session_{user_ind}"
            )
            # CHECK THE SESSION KEY of USER_SESSION  AND ADMIN adn CHECK USER ID
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
                user.is_active = False
                user.save(update_fields=["is_active"])
                login(request, user)
                cookie = Cookies(request.user.id, response)
                response = cookie.is_active(False)
                return response
            
            # GENERATE a referral link
            download_path = f"/api/v1/files/{file_record_list[0].special_link}/download/"
            
            referral_link = download_path
            # f"{request.build_absolute_uri(download_path)}"
            response = HttpResponse(status=status.HTTP_200_OK)
            cookie = Cookies((lambda: int(user_ind))(), response)
            response = cookie.empty_templete('referral_link', referral_link, max_age_=30 * 1000)
            # return JsonResponse({"special_link": referral_link})
            return response
        except (FileStorage.DoesNotExist, Exception) as e:
            return JsonResponse(
                {"error": f"Mistake => {e.__str__()}"},
                status=status.HTTP_404_NOT_FOUND
            )

    @staticmethod
    async def compare_twoFiles(
      link_ofNew_file: int, user_id: int,
      db_model: FileStorage
      ) -> bool:
        """
        TODO: We can check the one file without change and it, but with a change. \
The check will return the False.\
If we will be  check the one file with itself (and both files will be unchanged),\
 the check will return the True.
        :param index_old: int User id
        :param file: New file from the "request.FILES.get('file')"
        :return: True if file was equally  and the False when it can't be the equally
        """
        try:
            
            files_list = await sync_to_async(list)(db_model.objects.filter(user_id=user_id))
            if len(list(files_list)) == 0:
                return False
            hash_new_file = md5_chacker(f"{link_ofNew_file}")
            list_bool = [view for view in list(files_list) if hash_new_file == md5_chacker(view.file_path)]
            if len(list_bool) > 0:
                return True
            return False
        except Exception as e:
            return False
        finally:
            pass
