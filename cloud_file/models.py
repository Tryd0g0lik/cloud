"""
cloud_file/models.py
"""
from django.db import models
from django.core import validators as val
from django.utils.translation import gettext_lazy as _
import uuid

from cloud_user.models import UserRegister


class FileStorage(models.Model):
    user = models.ForeignKey(UserRegister, on_delete=models.CASCADE,
                             )
    original_name = models.CharField(_("File name"), max_length=100)
    size = models.PositiveIntegerField(_("File weight"),
                                       # validators=[
                                       #     val.MinValueValidator(limit_value=0)
                                       # ]
                                       )
    upload_date = models.DateTimeField(_("Date upload"),auto_now_add=True)
    last_downloaded = models.DateTimeField(_("Date download"), null=True,
                                           blank=True)
    comment = models.CharField(_("Mark"), blank=True, null=True)
    file_path = models.FileField(upload_to='media/uploads/',
                                 validators=[
#         val.validate_slug,
#         val.MaxLengthValidator(
#             limit_value=100,
#             message=_("Check the characters quantity. Max quantity of \
# characters is 100")),
#         val.MinValueValidator(
#             limit_value=3,
#             message=_("Check the characters quantity. Max quantity of \
# characters is 100")),
#
    ]
                                 )
    special_link = models.UUIDField(default=uuid.uuid4, editable=False,
                                    unique=True)

    def __str__(self):
        return self.original_name
