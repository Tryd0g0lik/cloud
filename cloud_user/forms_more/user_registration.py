"""Here is a registration form  for new users"""
import logging
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator, \
    MinLengthValidator, EmailValidator
from cloud_user.models import UserRegister
from django.utils.translation import gettext_lazy as _
from logs import configure_logging, Logger

configure_logging(logging.INFO)
log = logging.getLogger(__name__)

class MinValueValidato:
    pass


# class UsersRegistrationForm(forms.ModelForm, Logger):
class UsersRegistrationForm(forms.Form, Logger):
    '''
    TODO: A form for creating new users (registration a new user)
    `https://docs.djangoproject.com/en/5.0/topics/auth/customizing/#a-full-example`
    '''
    
    log.info(f" START")
    try:
        password1 = forms.CharField(label='Password',
                                    widget=forms.PasswordInput,
                                    validators=[
                                        EmailValidator()
                                    ]
                                    )
        password2 = forms.CharField(label='Password configuration',
                                    widget=forms.PasswordInput,
                                    error_messages = {
                                        "min_length":
                                          _("Слишком короткий. От 10 символов."),
                                        "max_length":
                                          _("Слишком длинный. До 30 символов.")
                                    },
                                    validators=[
                                      MaxLengthValidator(30),
                                      MinLengthValidator(10)
                                    ])
    except Exception as e:
        log.error(f"Mistake => {e.__str__()}")
        
    # class Meta:
    #     model = UserRegister
    #     fields = ["email", "username"]
    #     log.info("Was the Metta")

    def clean_password2(self):
        '''
        TODO: Check that the two password entries match
        :return:
        '''
        __text = f"[{self.print_class_name()}.{self.clean_password2.__name__}]: "
        log.info(f"{__text}START")
        try:
            password1 = self.cleaned_data.get('password1')
            password2 = self.cleaned_data.get('password2')
            
            if password1 and password2 and password1 != password2:
                raise ValidationError(_('Your password is not true'))
            __text = f"{__text} Your password is true. It is equal values"
            return password2[0:]
        except Exception as e:
            __text = f"{__text} Mistake => {e.__str__()}. \
Maybe need to check the passwords values from 'password1' and 'password2'."
        finally:
            if "Mistake" in __text:
                log.error(__text)
            else:
                log.info(__text)
            
#     def save(self, commit=True):
#         '''
#         TODO: Save the provided password  in hashed format
#         :param commit:
#         :return:
#         '''
#         __text = f"[{self.print_class_name()}.\
# {self.print_class_name.__name__}]:"
#         log.info(f"{__text} START")
#         try:
#             user = super().save(commit=False)
#             user.set_password(self.cleaned_data['password1'])
#             if commit:
#                 user.save()
#             __text = f"{__text} New user's object from \
# the user_cloud was preserved"
#             return user
#         except Exception as e:
#             __text = f"{__text} Mistake => {e.__str__()}. \
# New user's object from the user_cloud was not preserved"
#         finally:
#             if "Mistake" in __text:
#                 log.error(__text)
#             else:
#                 log.info(__text)
    