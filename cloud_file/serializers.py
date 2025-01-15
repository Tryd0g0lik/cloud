"""
cloud_file/serializers.py
Create serializer for a work with FileStorage model
"""
from rest_framework import serializers

from cloud_file.models import FileStorage


class FileStorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileStorage
        fields = ['id', 'original_name', 'size', 'upload_date', 'last_downloaded', 'comment', 'file_path', 'special_link']
