"""
cloud_file/views.py
"""
# from datetime import timezone

from django.core.files.base import ContentFile
from django.http import HttpResponse
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.cache import cache
from cloud.services import get_data_authenticate
from cloud_user.models import UserRegister
from .models import FileStorage
from .serializers import FileStorageSerializer
from django.core.files.storage import default_storage
from django.conf import settings
import os


class FileStorageViewSet(viewsets.ViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        
        if request.user.is_staff:
            # Если администратор, получаем файлы всех пользователей
            files = FileStorage.objects.all()
        else:
            # Получаем файлы только текущего пользователя
            files = FileStorage.objects.filter(user=request.user)
        
        serializer = FileStorageSerializer(files, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        # https://docs.djangoproject.com/en/4.2/topics/http/file-uploads/
        class DataCoockie:
            pass
        
        # GET user ID
        cookie_data = get_data_authenticate(request)
        user_ind = getattr(cookie_data, "id")
        cacher = DataCoockie()
        user_session = cache.get(f"user_session_{user_ind}")
        is_superuser = cache.get(f"is_superuser_{user_ind}")
        cache.close()
        # добавить куки и сделать свагер
        file_obj = request.FILES.get('file')
        if not file_obj or user_session != \
          getattr(cookie_data, f"user_session"):
            return Response(
                {"error": "No file provided."},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Сохранение файла на диск с уникальным именем
        file_path = default_storage.save(f'uploads/user_{user_ind}/{file_obj.name}', file_obj)
        # Создание записи в БД
        user = UserRegister.objects.filter(id=int(user_ind))
        file_record = FileStorage.objects.create(
            user= user[0], # request.user,
            original_name=file_obj.name,
            size=file_obj.size,
            file_path=file_path,
        )
        return Response(
            FileStorageSerializer(file_record).data,
            status=status.HTTP_201_CREATED
        )
    
    def destroy(self, request, pk=None):
        try:
            file_record = FileStorage.objects.get(pk=pk)
            if file_record.user != request.user and not request.user.is_staff:
                return Response(
                    {"error": "Permission denied."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Удаляем файл из хранилища и запись из БД
            default_storage.delete(file_record.file_path)
            file_record.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except FileStorage.DoesNotExist:
            return Response(
                {"error": "File not found."}, status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def rename(self, request, pk=None):
        new_name = request.data.get('new_name')
        if not new_name:
            return Response(
                {"error": "New name is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            file_record = FileStorage.objects.get(pk=pk)
            if file_record.user != request.user and not request.user.is_staff:
                return Response(
                    {"error": "Permission denied."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Переименование файла на диске и обновление записи в БД
            new_file_path = os.path.join(
                os.path.dirname(file_record.file_path.name), new_name
            )
            default_storage.save(
                new_file_path, default_storage.open(
                    file_record.file_path.name
                )
            )
            file_record.original_name = new_name
            file_record.file_path.name = new_file_path
            file_record.save()
            
            return Response(FileStorageSerializer(file_record).data)
        except FileStorage.DoesNotExist:
            return Response(
                {"error": "File not found."}, status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def update_comment(self, request, pk=None):
        comment = request.data.get('comment')
        try:
            file_record = FileStorage.objects.get(pk=pk)
            if file_record.user != request.user and not request.user.is_staff:
                return Response(
                    {"error": "Permission denied."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            file_record.comment = comment
            file_record.save()
            return Response(FileStorageSerializer(file_record).data)
        except FileStorage.DoesNotExist:
            return Response(
                {"error": "File not found."}, status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        from datetime import timezone
        try:
            file_record = FileStorage.objects.get(pk=pk)
            if file_record.user != request.user and not request.user.is_staff:
                return Response(
                    {"error": "Permission denied."},
                    status=status.HTTP_403_FORBIDDEN
                )
        
            # Обновляем дату последнего скачивания
            file_record.last_downloaded = timezone.now()
            file_record.save()
        
            response = HttpResponse(
                default_storage.open(file_record.file_path.name),
                content_type='application/octet-stream'
            )
            response[
                'Content-Disposition'] = f'attachment; filename="{file_record.original_name}"'
        
            return response
        except FileStorage.DoesNotExist:
            return Response(
                {"error": "File not found."}, status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def generate_link(self, request, pk=None):
        try:
            file_record = FileStorage.objects.get(pk=pk)
            
            # Генерация специальной ссылки (например, UUID или токен)
            special_link = f"{request.build_absolute_uri('/api/files/download/')}/{file_record.special_link}"
            
            return Response({"special_link": special_link})
        except FileStorage.DoesNotExist:
            return Response(
                {"error": "File not found."}, status=status.HTTP_404_NOT_FOUND
            )

# Важно: Не забудьте добавить маршруты для вашего ViewSet в urls.py.
