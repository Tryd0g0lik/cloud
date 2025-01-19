"""
cloud_file/views.py
"""
import asyncio
import json
import os

from asgiref.sync import sync_to_async
# from datetime import timezone

from django.core.files.base import ContentFile
from django.http import HttpResponse, JsonResponse
# from rest_framework import viewsets, permissions, status
from rest_framework import status
from adrf import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.cache import cache

from cloud.hashers import md5_chacker
from cloud.services import get_data_authenticate
from cloud_user.models import UserRegister
from .models import FileStorage
from .serializers import FileStorageSerializer
from django.core.files.storage import default_storage
from datetime import datetime

# instance = get_data_authenticate(request)


class FileStorageViewSet(viewsets.ViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    queryset = FileStorage.objects.all()
    serializer_class = FileStorageSerializer
    
    # @action(detail=True, url_path="", methods=["get"])
    # @action(detail=True, url_path="{pk}/", methods=["get"])
    async def list(self, request, *args, **kwargs) -> JsonResponse:
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
    
    async def retrieve(self, request, *args, **kwargs):
        status_data = []
        status_code = status.HTTP_200_OK
        files = []
        try:
            instance = await  sync_to_async(get_data_authenticate)(request)
            if kwargs["pk"] and int(kwargs["pk"]) == int(instance.id):
                files = await sync_to_async(list)(
                    FileStorage.objects.filter(id=int(kwargs["pk"]))
                )
                if len(files) == 0:
                    return JsonResponse({"error": "'pk' is invalid"},
                                        status=status.HTTP_400_BAD_REQUEST)
            else:
                status_data = {"error": "'pk' is invalid"}
                return JsonResponse(status_data,
                    status=status.HTTP_400_BAD_REQUEST
                    )
            serializer = self.serializer_class(files)
            status_data = serializer.data
            # if "[" in str(serializer.data):
            #     status_data = {"data": list(serializer.data)}
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
        time_path = f"card/{datetime.now().year}/{datetime.now().month}/{datetime.now().day}"
        # SAVE file
        await sync_to_async(default_storage.save)(f"{time_path}/{file_obj.name}", file_obj)
        # CHECK the file to file's duplication
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
            file_record = await sync_to_async(FileStorage.objects.acreate())(
                user= user_list.afirst(),
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
    
    async def destroy(self, request, pk=None):
        status_data = {}
        status_code =status.HTTP_204_NO_CONTENT
        try:
            file_record = await sync_to_async(list)(FileStorage.objects.filter(pk=pk))
            if len(file_record) == 0:
                return JsonResponse({"error": "'pk' invalid"},
                                    status=status.HTTP_400_BAD_REQUEST)
            
            if  \
              file_record[0].user.id != int(pk) or \
              (file_record[0].user.id == int(pk) and
               not file_record[0].user.is_staff):
                return Response(
                    {"error": "Permission denied."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # DELETE a single file from db
            await sync_to_async(default_storage.delete(file_record[0].file_path))
            await sync_to_async(file_record[0].adelete())
            status_code=status.HTTP_204_NO_CONTENT
        except FileStorage.DoesNotExist:
            status_data = {"error": "File not found."}
            status_code = status.HTTP_404_NOT_FOUND
        finally:
            return JsonResponse(status_data, status=status_code)

    @action(detail=True, url_path="api/v1/files/rename/<int:pk>",
            methods=['post'])
    async def rename(self, request, pk=None):
        new_name = request.data.get('new_name')
        if not new_name:
            return JsonResponse(
                {"error": "New name is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            file_record_list =\
                await sync_to_async(list)(FileStorage.objects.filter(pk=pk))
            
            if len(file_record_list) == 0 or\
              file_record_list[0].user != request.user and not request.user.is_staff:
                return JsonResponse(
                    {"error": "Permission denied."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Переименование файла на диске и обновление записи в БД
            new_file_path = os.path.join(
                os.path.dirname(file_record_list[0].file_path.name), new_name
            )
            default_storage.asave(
                new_file_path, default_storage.open(
                    file_record_list[0].file_path.name
                )
            )
            file_record_list[0].original_name = new_name
            file_record_list[0].file_path.name = new_file_path
            file_record_list[0].asave()
            
            return JsonResponse(self.serializer_class(file_record_list).data)
        except FileStorage.DoesNotExist:
            return JsonResponse(
                {"error": "File not found."}, status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['POST'])
    async def update_comment(self, request, pk=None):
        comment = request.data.get('comment')
        try:
            file_record_list = \
                await sync_to_async(list)(FileStorage.objects.filter(pk=pk))
            if len(file_record_list) == 0 or \
              file_record_list[0].user != request.user and \
              not request.user.is_staff:
                return JsonResponse(
                    {"error": "Permission denied."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            file_record_list[0].comment = comment
            file_record_list[0].asave()
            return JsonResponse(self.serializer_class(file_record_list[0]).data)
        except FileStorage.DoesNotExist:
            return JsonResponse(
                {"error": "File not found."}, status=status.HTTP_404_NOT_FOUND
            )
    
    # @action(detail=True, url_path="download/<int:pk>/", methods=['get'])
    @action(detail=True, url_name="api/v1/files/file_download/<int:pk>",
            methods=['GET'])
    async def download(self, request, pk=None):
        from datetime import timezone
        try:
            file_record_list = \
                await sync_to_async(list)(FileStorage.objects.filter(pk=pk))
            if len(file_record_list) == 0 or \
                file_record_list[0].user != request.user and\
              not request.user.is_staff:
                return JsonResponse(
                    {"error": "Permission denied."},
                    status=status.HTTP_403_FORBIDDEN
                )
        
            # Обновляем дату последнего скачивания
            file_record_list[0].last_downloaded = timezone.now()
            file_record_list[0].asave()
        
            response = HttpResponse(
                default_storage.open(file_record_list[0].file_path.name),
                content_type='application/octet-stream'
            )
            response['Content-Disposition'] = \
                f'attachment; filename="{file_record_list[0].original_name}"'
        
            return response
        except FileStorage.DoesNotExist:
            return JsonResponse(
                {"error": "File not found."}, status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, url_path="api/v1/files/referral_link/<int:pk>",
            methods=['GET'])
    async def generate_link(self, request, pk=None):
        try:
            
            file_record_list = \
                await sync_to_async(list)(FileStorage.objects.filter(pk=pk))
            
            # Генерация специальной ссылки (например, UUID или токен)
            special_link = \
            f"{request.build_absolute_uri('/api/files/download/')}/{file_record_list[0].special_link}"
            
            return JsonResponse({"special_link": special_link})
        except FileStorage.DoesNotExist:
            return JsonResponse(
                {"error": "File not found."}, status=status.HTTP_404_NOT_FOUND
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
# Важно: Не забудьте добавить маршруты для вашего ViewSet в urls.py.
