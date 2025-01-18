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
    serializer_class  = FileStorageSerializer
    async def list(self, request):
        
        if request.user.is_staff:
            # Если администратор, получаем файлы всех пользователей
            files = sync_to_async(list)(FileStorage.objects.all())
        else:
            # Получаем файлы только текущего пользователя
            files = sync_to_async(list)(FileStorage.objects.filter(user=request.user))
        
        serializer = self.serializer_class(files, many=True)
        return Response(serializer.data)
    
    async def create(self, request):
        # https://docs.djangoproject.com/en/4.2/topics/http/file-uploads/
        class DataCoockie:
            pass
        
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
        # Conservation a one file in serverby a path 'card/<year>/<month>/<day>/< file name >'
        time_path = f"card/{datetime.now().year}/{datetime.now().month}/{datetime.now().day}"
        await sync_to_async(default_storage.save)(f"{time_path}/{file_obj.name}", file_obj)
        # CHECK the file by double
        result_bool = await asyncio.create_task(
            FileStorageViewSet.compare_twoFiles(f"{time_path}/{file_obj.name}", int(user_ind), FileStorage)
        )
        # Create a line in db
        if not result_bool:
            await sync_to_async(default_storage.delete)(f"{time_path}/{file_obj.name}")
            time_path = time_path.replace("card/", "uploads/")
            # Re-conservation a file ( from over) in server by a path 'uploads/<year>/<month>/<day>/< file name >'
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
            #
            await sync_to_async(default_storage.delete)(f"{time_path}/{file_obj.name}")
        time_path = time_path.replace("card/", "uploads/")
        # Get the old file by a path 'uploads/<year>/<month>/<day>/< file name >'
        file_old_list = await sync_to_async(list)(FileStorage.objects.filter(file_path=f"{time_path}/{file_obj.name}"))
        if len(file_old_list) > 0:
            serializer = self.serializer_class(file_old_list[0])
            return JsonResponse(serializer.data,
                            status=status.HTTP_208_ALREADY_REPORTED)
        return JsonResponse(status=status.HTTP_400_BAD_REQUEST)
    
    async def destroy(self, request, pk=None):
        try:
            file_record = await sync_to_async(list)(FileStorage.objects.filter(pk=pk))
            if len(file_record) == 0:
                return JsonResponse({"error": "'pk' invalid"},
                                    status=status.HTTP_400_BAD_REQUEST)
            
            if  \
              file_record.user != request.user and \
              not request.user.is_staff:
                return Response(
                    {"error": "Permission denied."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Удаляем файл из хранилища и запись из БД
            await sync_to_async(default_storage.delete(file_record.file_path))
            await sync_to_async(file_record.delete())
            return JsonResponse(status=status.HTTP_204_NO_CONTENT)
        except FileStorage.DoesNotExist:
            return JsonResponse(
                {"error": "File not found."}, status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
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
    
    @action(detail=True, methods=['post'])
    async def update_comment(self, request, pk=None):
        comment = request.data.get('comment')
        try:
            file_record_list = \
                await sync_to_async(list)(FileStorage.objects.filter(pk=pk))
            if len(file_record_list) == 0or \
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
    
    @action(detail=True, methods=['get'])
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
    
    @action(detail=True, methods=['get'])
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
