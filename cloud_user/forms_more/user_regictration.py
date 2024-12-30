from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator, \
    MinLengthValidator, EmailValidator
from cloud.models import UserRegister
from django.utils.translation import gettext_lazy as _


class MinValueValidato:
    pass


class UsersRegistrationForm(forms.ModelForm):
    '''
    TODO: A form for creating new users (registration a new user)
    `https://docs.djangoproject.com/en/5.0/topics/auth/customizing/#a-full-example`
    '''

    password1 = forms.CharField(label='Password', widget=forms.PasswordInput,
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

    class Meta:
        model = UserRegister
        fields = ["email", "username"]

    def clean_password2(self):
        '''
        TODO: Check that the two password entries match
        :return:
        '''

        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError('Пароль не сходится')
        return password2[0:]

    def save(self, commit=True):
        '''
        TODO: Save the provided password  in hashed format
        :param commit:
        :return:
        '''
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user
