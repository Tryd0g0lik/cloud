"""
cloud_file/views.py
Here, interface of file storage.
"""
import asyncio
from typing import TypedDict
import os

from asgiref.sync import sync_to_async
from django.http import HttpResponse, JsonResponse
from rest_framework import status
from adrf import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.cache import cache
# from django.views.decorators.csrf import csrf_exempt
from cloud.hashers import md5_chacker
from cloud.services import get_data_authenticate
from cloud_user.models import UserRegister
from .models import FileStorage
from .serializers import FileStorageSerializer
from django.core.files.storage import default_storage
from datetime import datetime, timezone

class Kwargs(TypedDict):
    pk: int
class PKStr(TypedDict):
    pk: str
class FileStorageViewSet(viewsets.ViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    queryset = FileStorage.objects.all()
    serializer_class = FileStorageSerializer
    
    async def list(self, request, *args, **kwargs: Kwargs) -> JsonResponse:
        status_data: [dict, list] = []
        status_code = status.HTTP_200_OK
        files = []
        try:
            instance = await sync_to_async(get_data_authenticate)(request)
            files = await sync_to_async(list)(
                FileStorage.objects.filter(
                    user_id=int(instance.id)
                    ))
            if len(files) == 0:
                return JsonResponse(status=status.HTTP_400_BAD_REQUEST)
            # /* -----------  lambda  ----------- */
            user_is_staff = await sync_to_async(lambda: files[0].user.is_staff)()
            if user_is_staff :
                # Если администратор, получаем файлы всех пользователей
                files = await sync_to_async(list)(FileStorage.objects.all())
            elif not user_is_staff and int(kwargs["pk"]) == int(instance.id) :
                # Получаем файлы только текущего пользователя
                files = await sync_to_async(list)(FileStorage.objects\
                                            .filter(user_id=int(instance.id)))
            else:
                files = []
            serializer = self.serializer_class(files, many=True)
            status_data = serializer.data
            if "[" in str(serializer.data):
                status_data = {"data": list(serializer.data)}
        except Exception as e:
            status_data = {"error": f"[{FileStorageViewSet.__class__.list.__name__}]: \
            Mistake => {e.__str__()}"}
            status_code = status.HTTP_400_BAD_REQUEST
        finally:
            return JsonResponse(status_data,
                status=status_code)
    
    async def retrieve(self, request, *args, **kwargs: Kwargs):
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
            # GET  data of COOKIE (is_superuser_* & user_session_*)
            instance = await sync_to_async(get_data_authenticate)(request)
            if kwargs["pk"]:
                files = await sync_to_async(list)(
                    FileStorage.objects.filter(id=int(kwargs["pk"]))
                )
                #  await sync_to_async(lambda: files[0].user.is_staff)()
                if len(files) == 0:
                    return JsonResponse({"error": "'pk' is invalid"},
                                        status=status.HTTP_400_BAD_REQUEST)
                # Get data of line from db
                # /* -----------  lambda  ----------- */
                user_id_fromFile =\
                    await sync_to_async(lambda: files[0].user.id)()
                user_is_staff_fromFile = \
                    await sync_to_async(lambda: files[0].user.is_staff)()
                # Check id - authentification
                if (int(instance.id) != user_id_fromFile) and \
                  not user_is_staff_fromFile:
                    return JsonResponse(
                        {"error": "There is no access"},
                        status=status.HTTP_400_BAD_REQUEST
                        )
                
            else:
                status_data = {"error": "'pk' is invalid"}
                return JsonResponse(status_data,
                    status=status.HTTP_400_BAD_REQUEST
                    )
            serializer = self.serializer_class(files[0])
            status_data = serializer.data
            return JsonResponse(
                status_data,
                status=status_code
            )
        except Exception as e:
            status_data = {
                "error": f"[{FileStorageViewSet.__class__.retrieve.__name__}]: \
                       Mistake => {e.__str__()}"}
            status_code = status.HTTP_400_BAD_REQUEST
        
            return JsonResponse(
                status_data,
                status=status_code
                )
        

    async def create(self, request):
        # https://docs.djangoproject.com/en/4.2/topics/http/file-uploads/
       
        # GET the user ID from COOKIE
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
            return JsonResponse(
                {"error": "No file provided."},
                status=status.HTTP_400_BAD_REQUEST
            )
        """
        Conservation a one file in serverby by path \
        'card/<year>/<month>/<day>/< file name >'
        First, we need to check the duplication file.  For this, we save the file \
        by path 'card/...'.
        
        """
        time_path = f"card/{user_ind}/{datetime.now().year}/{datetime.now().month}/{datetime.now().day}"
        
        # SAVE file
        await sync_to_async(default_storage.save)(f"{time_path}/{file_obj.name}", file_obj)
        # CHECK the file on a file's duplication
        result_bool = await asyncio.create_task(
            FileStorageViewSet.compare_twoFiles(f"{time_path}/{file_obj.name}", int(user_ind), FileStorage)
        )
        # CREATE A LINE in db if NOT duplication
        if not result_bool:
            await sync_to_async(default_storage.delete)(f"{time_path}/{file_obj.name}")
            time_path = time_path.replace("card/", "uploads/")
            # Re-save a file ( from over) in server by a path 'uploads/<year>/<month>/<day>/< file name >'
            file_path = await sync_to_async(default_storage.save)(f"{time_path}/{file_obj.name}", file_obj)
            user_list = await sync_to_async(list)(UserRegister.objects.filter(id=int(user_ind)))
            file_record = await sync_to_async(FileStorage.objects.create)(
                user= user_list[0],
                original_name=file_obj.name,
                size=file_obj.size,
                file_path="%s" % file_path,
            )
            serializer = self.serializer_class(file_record)
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
    
    async def destroy(self, request, pk: Kwargs = None):
        """
        TODO: This is for delete a single file's line from db. .
        :param request:
        :param pk: integer from single line of db, for changing
        :return:
        """
        status_data = {}
        status_code =status.HTTP_204_NO_CONTENT
        # GET the user ID from COOKIE
        cookie_data = await sync_to_async(get_data_authenticate)(request)
        user_ind = getattr(cookie_data, "id")
        try:
            
            file_list = await sync_to_async(list)(FileStorage.objects.filter(id=pk))
            if len(file_list) == 0:
                return JsonResponse({"error": "'pk' invalid"},
                                    status=status.HTTP_400_BAD_REQUEST)
            # Get data of line from db
            # /* -----------  lambda  ----------- */
            user_id_fromFile = \
                await sync_to_async(lambda: file_list[0].user.id)()
            user_is_staff_fromFile = \
                await sync_to_async(lambda:  file_list[0].user.is_staff)()
  
            if  \
              user_id_fromFile != user_ind and \
              not user_is_staff_fromFile:
                return Response(
                    {"error": "Permission denied."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # DELETE a single file from db
            await sync_to_async(default_storage.delete)(f"{file_list[0].file_path}")
            await sync_to_async(file_list[0].delete)()
            status_code=status.HTTP_204_NO_CONTENT
        except FileStorage.DoesNotExist:
            status_data = {"error": "File not found."}
            status_code = status.HTTP_404_NOT_FOUND
        finally:
            return JsonResponse(status_data, status=status_code)

    @action(detail=True, url_name="rename",
            methods=['post'])
    async def rename(self, request, pk: Kwargs = None):
        """
        TODO: This is for rename a single file's line from db. .
        :param request:
        :param pk: integer from single line of db, for changing
        :return:
        """
        new_name = request.data.get('new_name')
        # GET the user ID from COOKIE
        cookie_data = await sync_to_async(get_data_authenticate)(request)
        user_ind = getattr(cookie_data, "id")
        if not new_name:
            return JsonResponse(
                {"error": "New name is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            file_record_list =\
                await sync_to_async(list)(FileStorage.objects.filter(pk=pk))
            
            if len(file_record_list) == 0 :
                # Get data of line from db
                # /* -----------  lambda  ----------- */
                return JsonResponse(
                    {"error": "Check the 'pk"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # GET old data from db
            user_id_fromFile = \
                await sync_to_async(lambda: file_record_list[0].user.id)()
            user_is_staff_fromFile = \
                await sync_to_async(
                    lambda: file_record_list[0].user.is_staff
                    )()
            user_original_name_fromFile =\
                await sync_to_async(lambda: file_record_list[0].original_name)()
            file_extencion = str(user_original_name_fromFile).split(".")[-1]
            # CHECK of user
            if user_id_fromFile != int(user_ind) and \
              not user_is_staff_fromFile:
                return JsonResponse(
                    {"error": "Permission denied."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # RENAME file
            new_file_path = (file_record_list[0].file_path.path).replace(
                          file_record_list[0].file_path.name.split("/")[-1],
                          f"{new_name}.{file_extencion}")
            os.rename(file_record_list[0].file_path.path, new_file_path)
            
            # GET path for the db
            file_record_list[0].original_name = f"{new_name}.{file_extencion}"
            file_record_list[0].file_path.name = \
                "uploads" + new_file_path.replace("\\", "/").replace(r"//", "/")\
                    .split("uploads")[-1]
            await sync_to_async(file_record_list[0].save)()
            
            return JsonResponse(self.serializer_class(file_record_list[0]).data)
        except (FileStorage.DoesNotExist, Exception) as e:
            return JsonResponse(
                {"error": f"Mistake => {e.__str__()}"},
                status=status.HTTP_404_NOT_FOUND
            )

    # @csrf_exempt
    @action(detail=True,
            url_name="comment", methods=['POST'])
    async def update_comment(self, request, pk: Kwargs = None):
        new_comment = request.data.get('comment')
        # http://127.0.0.1:8000/api/v1/files/31/update_comment/
        try:
            file_record_list = \
                await sync_to_async(list)(FileStorage.objects.filter(pk=pk))
            if len(file_record_list) == 0:
                return JsonResponse(
                    {"error": "File not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
            # GET the user ID from COOKIE
            cookie_data = await sync_to_async(get_data_authenticate)(
                request
                )
            user_ind = getattr(cookie_data, "id")
            user_id_fromFile = \
                await sync_to_async(lambda: file_record_list[0].user.id)()
            if user_id_fromFile != int(user_ind):
                return JsonResponse(
                    {"error": "Permission denied."},
                    status=status.HTTP_403_FORBIDDEN
                )
        
            file_record_list[0].comment = new_comment
            await sync_to_async(file_record_list[0].save)()
            
            return JsonResponse(self.serializer_class(file_record_list[0]).data)
        except FileStorage.DoesNotExist:
            return JsonResponse(
                {"error": "File not found."}, status=status.HTTP_404_NOT_FOUND
            )
    
    # @action(detail=True, url_path="download/<int:pk>/", methods=['get'])
    @action(detail=True, url_name="download",
            methods=['GET'])
    async def download(self, request, pk: PKStr = None):
        from datetime import timezone
        try:
            # GET the user ID from COOKIE
            cookie_data = await sync_to_async(get_data_authenticate)(request)
            user_ind = getattr(cookie_data, "id")
            # GET line from db
            file_record_list = \
                await sync_to_async(list)(FileStorage.objects\
                                          .filter(special_link=pk))
            if len(file_record_list) == 0:
                # Get data of line from db
                # /* -----------  lambda  ----------- */
                return JsonResponse(
                    {"error": "Check the 'pk"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Here is not a check of user
            
            # Update the 'last_downloaded' from line
            file_record_list[0].last_downloaded = datetime.utcnow()
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
    
    @action(detail=True, url_name="generate_link",
            methods=['GET'])
    async def generate_link(self, request, pk: Kwargs = None):
        try:
            # GET the user ID from COOKIE
            cookie_data = await sync_to_async(get_data_authenticate)(request)
            user_ind = getattr(cookie_data, "id")
            file_record_list = \
                await sync_to_async(list)(FileStorage.objects.filter(pk=pk))
            if len(file_record_list) == 0 :
                # Get data of line from db
                # /* -----------  lambda  ----------- */
                return JsonResponse(
                    {"error": "Check the 'pk"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # GET old data from db
            user_id_fromFile = \
                await sync_to_async(lambda: file_record_list[0].user.id)()
            user_is_staff_fromFile = \
                await sync_to_async(
                    lambda: file_record_list[0].user.is_staff
                )()
            # CHECK of user
            if user_id_fromFile != int(user_ind) and \
              not user_is_staff_fromFile:
                return JsonResponse(
                    {"error": "Permission denied."},
                    status=status.HTTP_403_FORBIDDEN
                )
            # GENERATE a spacial link
            download_path = f"/api/files/{file_record_list[0].special_link}/download/"
            special_link = \
            f"{request.build_absolute_uri(download_path)}"
            
            return JsonResponse({"special_link": special_link})
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

