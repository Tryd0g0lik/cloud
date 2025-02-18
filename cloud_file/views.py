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
from rest_framework import status
from adrf import viewsets
from rest_framework.decorators import action
from django.core.cache import cache

from cloud.cookies import Cookies
from cloud.hashers import md5_chacker
from cloud.services import get_data_authenticate
from cloud_user.models import UserRegister
from project.settings import (SESSION_COOKIE_AGE, SESSION_COOKIE_HTTPONLY, \
    SESSION_COOKIE_SECURE, SESSION_COOKIE_SAMESITE)

from .models import FileStorage
from .serializers import FileStorageSerializer
from django.core.files.storage import default_storage
from datetime import datetime
from project import decorators_CSRFToken
from project import use_CSRFToken
class FileStorageViewSet(viewsets.ViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    queryset = FileStorage.objects.all()
    serializer_class = FileStorageSerializer

    @decorators_CSRFToken(True)
    async def list(self, request, *args, **kwargs) -> JsonResponse:
        status_data: [dict, list] = []
        status_code = status.HTTP_200_OK
        files = []
        
        try:
            if request.user.is_authenticated:
                user_session_client = getattr(request.COOKIES, "user_session")
                # GET use-session from the cache  (our
                # cecher table from settings.py)
                user_session_db = await sync_to_async(cache.get)(
                    f"user_session_{request.user.id}"
                )
                # CHECK THE KEY of USER_SESSION
                if user_session_db != user_session_client:
                    return JsonResponse({"data": ["User is not authenticated"]},
                                        status=status.HTTP_403_FORBIDDEN)
                instance = await sync_to_async(get_data_authenticate)(request)
                
                # IF USER IS ADMIN - RETURN ALL FILES FROM ALL USERS
                if request.user.is_staff:
                    files = await sync_to_async(list)(FileStorage.objects.all())
                elif not request.user.is_staff:
                    # #
                    files = await sync_to_async(list)(FileStorage.objects\
                                                .filter(user_id=int(instance.id)))
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
    
    @decorators_CSRFToken(True)
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
                user_session_client = getattr(request.COOKIES, "user_session")
                # GET use-session from the ceche (our
                # cecher table from settings.py)
                user_session_db = await sync_to_async(cache.get)(
                    f"user_session_{request.user.id}")
                # CHECK THE SESSION KEY of USER_SESSION
                if user_session_db != user_session_client:
                    return JsonResponse(
                        {"data": ["User is not authenticated"]},
                        status=status.HTTP_403_FORBIDDEN
                        )
                # CHECK USER ID
                if request.user.id != int(kwargs["pk"]) \
                  and not request.user.is_staff:
                    return JsonResponse(
                        {"error": "There is no access"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                # GET FILES FROM SINGLE USER
                files = await sync_to_async(list)(
                    FileStorage.objects.filter(user_id=int(kwargs["pk"]))
                )
                
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
            elif not request.user.is_authenticated:
                # NOT LOGGEN IN
                return JsonResponse({"detail": "User is not authenticated"},
                    status=status.HTTP_400_BAD_REQUEST
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

    @decorators_CSRFToken(True)
    async def create(self, request):
        # if not request.META.get("HTTP_X_CSRFTOKEN") or not \
        #   request.COOKIES.get('csrftoken') or\
        #   request.COOKIES.get(settings.CSRF_COOKIE_NAME) != request.META.get("HTTP_X_CSRFTOKEN"):
        #     return JsonResponse(
        #         {"detail": "CSRF verification failed"}, status=403
        #         )
        
        cookie_data = await sync_to_async(get_data_authenticate)(request)
        user_ind = getattr(cookie_data, "id")
        user_session = await sync_to_async(cache.get)(f"user_session_{user_ind}")
        cache.close()
        # GET the file's data
        file_obj = request.FILES.get('file')
        if not file_obj:
            return JsonResponse({"error": "No file provided"},
                                status=status.HTTP_400_BAD_REQUEST)
        if not file_obj or user_session != \
          getattr(cookie_data, f"user_session"):
            response = JsonResponse(
                {"error": "No file provided."},
                status=status.HTTP_400_BAD_REQUEST
            )
            response.set_cookie(
                "is_active",
                False,
                max_age=SESSION_COOKIE_AGE,
                httponly=SESSION_COOKIE_HTTPONLY,
                secure=SESSION_COOKIE_SECURE,
                samesite=SESSION_COOKIE_SAMESITE
            )
            return response
        """
        Conservation a one file in serverby by path \
        'card/<year>/<month>/<day>/< file name >'
        First, we need to check the duplication file.  For this, we save the file \
        by path 'card/...'.
        
        """
        time_path = f"card/{user_ind}/{datetime.now().year}/{datetime.now().month}/{datetime.now().day}"
        
        # SAVE file
        await sync_to_async(default_storage.save)\
            (f"{time_path}/{file_obj.name}", file_obj)
        # CHECK the file on a file's duplication
        result_bool = await asyncio.create_task(
            FileStorageViewSet.compare_twoFiles(f"{time_path}/{file_obj.name}", int(user_ind), FileStorage)
        )
        # CREATE A LINE in db if NOT duplication
        if not result_bool:
            await sync_to_async(default_storage.delete)(f"{time_path}/{file_obj.name}")
            time_path = time_path.replace("card/", "uploads/")
            # Re-save a file ( from over) in server by a path 'uploads/<year>/<month>/<day>/< file name >'
            file_path = await asyncio.create_task(
                sync_to_async(default_storage.save)\
                    (f"{time_path}/{file_obj.name}", file_obj)
            )
            user_list = await asyncio.create_task(
                sync_to_async(list)\
                    (UserRegister.objects.filter(id=int(user_ind)))
            )
            file_record = await sync_to_async(FileStorage.objects.create)(
                user= user_list[0],
                original_name=file_obj.name,
                size=file_obj.size,
                file_path="%s" % file_path,
            )
            serializer = FileStorageSerializer(file_record)
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # If, we found the file's dupolication
            await sync_to_async(default_storage.delete)(f"{time_path}/{file_obj.name}")
        time_path = time_path.replace("card/", "uploads/")
        # Get the old file by path 'uploads/<year>/<month>/<day>/< file name >'
        # /* --------------- А если файл переименован?? --------------- */
        file_old_list = \
            await sync_to_async(list)(FileStorage.objects\
                                      .filter(original_name=f"{file_obj.name}"))
        if len(file_old_list) > 0:
            serializer = self.serializer_class(file_old_list[0])
            return JsonResponse(serializer.data,
                            status=status.HTTP_208_ALREADY_REPORTED)
        # If something what wrong
        return JsonResponse({"error": "The wrong, incorrect request"},
                            status=status.HTTP_400_BAD_REQUEST)
    
    async def destroy(self, request, *args):
        return sync_to_async(JsonResponse)({"error": "The wrong, incorrect request"})
    
    
    @action(detail=True, url_name="delete", methods=["PUT"])
    @decorators_CSRFToken(True)
    async def remove(self, request, **kwargs):
        """
        TODO: This is for delete a single file's line from db. .
        :param request:
        :param pk: integer from single line of db, for changing
        :return:
        """
        status_data = {}
        status_code =status.HTTP_204_NO_CONTENT
        files_id_list = json.loads(request.body)["files"]
        # GET the user ID from COOKIE
        # cookie_data = await asyncio.create_task(
        #     sync_to_async(get_data_authenticate)(request)
        # )
        try:
            
            file_list = [await asyncio.create_task(
                sync_to_async(list)(FileStorage.objects.filter(id=index))
            ) for index in files_id_list]
            file_list = [file[0] for file in file_list]
            if len(file_list) == 0:
                return sync_to_async(JsonResponse)({"error": "'pk' invalid"},
                                    status=status.HTTP_400_BAD_REQUEST)
            # CREATE TASK ASYNC
            tasks = []
            for file in file_list:
                tasks.append(
                    sync_to_async(default_storage.delete)(f"{file.file_path}")
                    )
                tasks.append(sync_to_async(file.delete)())
            #  DELETE OLD FILES (ALL TASKS)
            await asyncio.gather(*tasks)
            status_code=status.HTTP_204_NO_CONTENT
        except FileStorage.DoesNotExist:
            status_data = {"error": "File not found."}
            status_code = status.HTTP_404_NOT_FOUND
        finally:
            return JsonResponse(status_data, status=status_code)

    
    @action(detail=True, url_name="rename",
            methods=['post'])
    @decorators_CSRFToken(True)
    async def rename(self, request, **kwargs):
        """
        TODO: This is for rename a single file's line from db. .
        :param request:
        :param pk: integer from single line of db, for changing
        :return:
        """
        new_name = json.loads(request.body).get('new_name')
        file_id = json.loads(request.body).get('fileId')
        
        # GET the user ID from COOKIE (cookie_data the object
        cookie_data = await sync_to_async(get_data_authenticate)(request)
        if not new_name:
            return JsonResponse(
                {"error": "New name is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            file_record_list =\
                await sync_to_async(list)(FileStorage.objects
                                          .filter(user_id=int(kwargs['pk']))
                                          .filter(id=int(file_id)))
            # CHER THE NEW NAME OF FILE DUPLICATION
            file_name_duplication = await sync_to_async(list)(FileStorage.objects
                                          .filter(user_id=int(kwargs['pk']))
                                          .filter(original_name=new_name))
            if len(file_name_duplication) != 0:
                return JsonResponse(
                    {"detail": "The file with this name already exists."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if len(file_record_list) == 0 :
                # Get data of line from db
                # /* -----------  lambda  ----------- */
                return JsonResponse(
                    {"error": "Check the 'pk"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # GET use-session from the cache (table from db sessionю
            # It is our the caher)
            user_session_db = await sync_to_async(cache.get)(
                f"user_session_{kwargs['pk']}"
            )
            user_session_fromClient = cookie_data.user_session
            # CHECK of session/authorisation
            if user_session_fromClient != user_session_db:
                response = JsonResponse(
                    {"detail": "Permission denied."},
                    status=status.HTTP_403_FORBIDDEN
                )
                cookie = Cookies((lambda: int(kwargs['pk']))(), response)
                response = cookie.is_active(
                    is_active=False, max_age_=24 * 60 * 60
                    )
                return response
            # GET old data from db
            user_id_fromFile = \
                await asyncio.create_task(
                    sync_to_async(lambda: file_record_list[0].user.id)()
                )
            user_is_staff_fromFile = \
                await asyncio.create_task(
                    sync_to_async(
                    lambda: file_record_list[0].user.is_staff
                    )()
                )
            user_original_name_fromFile =\
                await asyncio.create_task(
                    sync_to_async(lambda: file_record_list[0].original_name)()
                )
            file_extencion = str(user_original_name_fromFile).split(".")[-1]
            # CHECK of user
            if user_id_fromFile != int(kwargs["pk"]) and not user_is_staff_fromFile:
                return JsonResponse(
                    {"detail": "Permission denied."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # RENAME file
            new_file_path = (file_record_list[0].file_path.path).replace(
                          file_record_list[0].file_path.name.split("/")[-1],
                new_name) # f"{new_name}.{file_extencion}"
            os.rename(file_record_list[0].file_path.path, new_file_path)
            
            # GET path for the db
            
            file_record_list[0].original_name = new_name #f"{new_name}.{file_extencion}"
            file_record_list[0].file_path.name = \
                "uploads" + new_file_path.replace("\\", "/").replace(r"//", "/")\
                    .split("uploads")[-1]
            await sync_to_async(file_record_list[0].save)()
            
            return JsonResponse(self.serializer_class(file_record_list[0]).data)
        except (FileStorage.DoesNotExist, Exception) as e:
            return JsonResponse(
                {"detail": f"Mistake => {e.__str__()}"},
                status=status.HTTP_404_NOT_FOUND
            )

    #
    @action(detail=True,
            url_name="comment", methods=['PATCH'])
    @decorators_CSRFToken(True)
    async def update_comment(self, request,  **kwargs):
        new_comment = json.loads(request.body).get('comment')
        # http://127.0.0.1:8000/api/v1/files/31/update_comment/
        file_id = json.loads(request.body).get('fileId')
        if file_id == None or new_comment == None:
            return sync_to_async(JsonResponse)(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        try:
            file_record_list = \
                await sync_to_async(list)(FileStorage.objects.filter(user_id=kwargs["pk"]).filter(pk=int(file_id)))
            if len(file_record_list) == 0:
                return sync_to_async(JsonResponse)(
                    {"error": "User not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
                
            file_record_list[0].comment = new_comment
            await sync_to_async(file_record_list[0].save)()
            
            return await sync_to_async(JsonResponse)(self.serializer_class(file_record_list[0]).data)
        except FileStorage.DoesNotExist:
            return await sync_to_async(JsonResponse)(
                {"error": "File not found."}, status=status.HTTP_404_NOT_FOUND
            )
    
    # @action(detail=True, url_path="download/<int:pk>/", methods=['get'])
    
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
    @decorators_CSRFToken(True)
    async def referral_links(self, request, **wargs):
        try:
            # GET the user ID from COOKIE
            cookie_data = await sync_to_async(get_data_authenticate)(request)
            user_ind = getattr(cookie_data, "id")
            file_id = request.COOKIES.get("fileId")
            # file_id = getattr(cookie_data, "fileId")
            file_record_list = \
                await sync_to_async(list)(FileStorage.objects.filter(user_id=int(wargs["pk"])).filter(pk=int(file_id)))
            if len(file_record_list) == 0 :
                # Get data of line from db
                # /* -----------  lambda  ----------- */
                return JsonResponse(
                    {"error": "Check the 'pk"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # GET old data from db
            user_id_fromFile = \
                await asyncio.create_task(
                    sync_to_async(lambda: file_record_list[0].user.id)()
                )
            user_is_staff_fromFile = \
                await asyncio.create_task(
                    sync_to_async(
                    lambda: file_record_list[0].user.is_staff
                )()
                )
           
            user_session_fromFile = getattr(cookie_data, "user_session")
            # GET use-session from the ceche (table from db session)
            user_session_db = await sync_to_async(cache.get)(
                f"user_session_{user_ind}"
                )
            
            # CHECK of user/ This when the user id (from cookie of client)
            # not equals user id from db
            if (lambda: user_id_fromFile)() != (lambda: int(user_ind))() and \
              not user_is_staff_fromFile:
                response = JsonResponse(
                    {"error": "Permission denied."},
                    status=status.HTTP_403_FORBIDDEN
                )
                cookie = Cookies((lambda: int(user_ind))(), response)
                response = cookie.is_active(is_active=False)
                return response
            
            # CHECK of session/authorisation
            if user_session_fromFile != user_session_db:
                response =  JsonResponse(
                    {"error": "Permission denied."},
                    status=status.HTTP_403_FORBIDDEN
                )
                cookie = Cookies((lambda: int(user_ind))(), response)
                response = cookie.is_active(is_active=False, max_age_=30 * 1000)
              
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



