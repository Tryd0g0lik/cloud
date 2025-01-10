# import logging
# from django import forms
# from django.core.exceptions import ValidationError
# from django.core.validators import MaxLengthValidator, \
#     MinLengthValidator, EmailValidator
# from django.utils.translation import gettext_lazy as _
# from logs import configure_logging, Logger
#
# configure_logging(logging.INFO)
# log = logging.getLogger(__name__)
#
# # class RegisterUserForm(forms.ModelForm):
# class LoginForm(forms.Form, Logger):
#     '''
#    TODO: A form for creating new users (registration a new user)
#    `https://docs.djangoproject.com/en/5.0/topics/auth/customizing/#a-full-example`
#    '''
#
#     log.info(f" START")
#     try:
#         email = forms.CharField(
#             required=True,
#             widget=forms.EmailInput,
#             label=_("Email"),
#             help_text=_("Email of user is unique. Max length is 320\
#  characters"),
#             validators=[
#                 EmailValidator(
#                     massage=_("Check the your email. Email of user is \
# unique. Max length is 320 characters")
#                 )
#             ]
#             )
#         password = forms.CharField(
#             label=_('Password configuration'),
#             widget=forms.PasswordInput,
#             error_messages={
#                 "min_length":
#                     _("Your password is a very short. Min length is \
# 10 characters."),
#                 "max_length":
#                     _("Your password is a very long. Max length is \
# 128 character.")
#             },
#             validators=[
#                 MaxLengthValidator(30),
#                 MinLengthValidator(128)
#             ],
#             help_text='Пароль'
#             )
#     except Exception as e:
#         __text = f"Mistake => {e.__str__()}"
#         log.error(__text)
#         raise ValidationError(__text)
