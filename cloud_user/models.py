"""
cloud_user/models.py
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core import validators as val
# Create your models here.
from django.contrib.auth.models import AbstractUser


# Create your models here.

class UserRegister(AbstractUser):
    """
       TODO: Here is a new default table for the user's registration for project.
           Here, we add new fields for the user registration.
       :param is_activated: bool. This is activation a new account after the \
           authentication. By link from the email of User, we make authentication.
       :param send_messages: bool. This is email's message, we sent to \
           the single user. His is the new user from the registration.
       :param username: str. Max length is 150 characters. This is unique\
           name of user
       :param first_name: str or None. Max length is 150 characters.
       :param last_name: str or None. Max length is 150 characters.
       :param last_login: str or None, format date-time.
       :param email: str. User email. Max length is 320 characters.
       :param is_staff: bool. Designates whether the user can log into \
           this admin site.
       :param is_active: bool. Designates whether this user should be treated \
           as active.
       :param date_joined: date. Date of registration.
       :param is_superuser: bool. Designates that this user has \
           all permissions. He is the admin site and only one.
       :param groups:
       :param  password: str. Max length of characters is 128 and min is 3.
       """
    last_name = models.CharField(_("last name"), max_length=150, null=True,
                                 blank=True)
    first_name = models.CharField(_("first name"), max_length=150, null=True,
                                  blank=True)
    email = models.EmailField(help_text=_("email address"),
                              blank=False,
                              unique=True,)
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='%(class)s_groups',
        blank=True,
        help_text=_('The groups this user belongs to. A user will get all permissions '
'granted to each of their groups.'),
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='%(class)s_user_permissions',
        # Уникальное имя для обратной связи
        blank=True,
        help_text=_('Specific permissions for this user.'),
        verbose_name='user permissions'
    )
    is_activated = models.BooleanField(
        default=False,
        verbose_name=_('After activation'),
        help_text=_("Part of the user registration. Message \
is sending to the email. В сообщении ссылка для подтверждения пользователя."),
    )
    send_messages = models.BooleanField(
        default=False,
        verbose_name='Слать оповещение',
        help_text=_("Part is registration of new user.It is message sending \
to user's email. User indicates his email at the registrations moment.")
    )
    
    class Meta(AbstractUser.Meta):
        indexes = [
            models.Index(fields=["is_activated"], name="activated_index")
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['username'], name='unique_username'
                )
        ]
        
    @property
    def is_authenticated(self) -> bool:
        """
         TODO: Read-only.  This is method which is always True (as opposed \
            to AnonymousUser.is_authenticated which is always False). This is\
            a way to tell if the user has been authenticated. This does not\
            imply any permissions and doesn’t check if the user is active or\
            has a valid session. Even though normally you will check this\
            attribute on request.user to find out whether it has been \
            populated by the.
            From user 'object.is_authenticated()'
        https://docs.djangoproject.com/en/5.1/topics/auth/customizing/\
#django.contrib.auth.models.AbstractBaseUser.is_authenticated
        :return: bool
        """
        if self.is_active:
            return True
        return False
        
    

