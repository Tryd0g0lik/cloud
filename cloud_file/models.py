"""
cloud_file/models.py
"""
from django.db import models
from django.contrib.auth.models import User
import uuid

class FileStorage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    original_name = models.CharField(max_length=255)
    size = models.PositiveIntegerField()
    upload_date = models.DateTimeField(auto_now_add=True)
    last_downloaded = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(blank=True, null=True)
    file_path = models.FileField(upload_to='uploads/')
    special_link = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.original_name
