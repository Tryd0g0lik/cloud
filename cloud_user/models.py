from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser


# Create your models here.

class UserRegister(AbstractUser):
    is_activated = models.BooleanField(
        default=True,
        verbose_name='Прошел активацию'
    )
    send_messages = models.BooleanField(
        default=True,
        verbose_name='Слать оповещение'
    )
    
    class Meta(AbstractUser.Meta):
        indexes = [
            models.Index(fields=["is_activated"], name="activated_indx")
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['username'], name='unique_username'
                )
        ]

