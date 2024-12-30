from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError

from cloud_user.apps import user_registered
from cloud_user.models import UserRegister


class RegisterUserForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        label='Адрес электронной почты'
        )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput,
        help_text='Пароль'
        )
    password2 = forms.CharField(
        label='Пароль (повторно)',
        widget=forms.PasswordInput,
        help_text='Введение тот же самый пароль ещё \
раз для проверки'
        )
    
    def clean_password(self):
        password1 = self.cleaned_data['password1']
        if password1:
            password_validation.validate_password(password1)
        return password1
    
    def clean(self):
        super().clean()
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password_validation and password2 and password1 != password2:
            errors = {'password2': ValidationError(
                'Введенные пароли не \
совпадают', code='password_mismatch'
                )}
            raise ValidationError(errors)
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.is_active = False
        user.is_activated = False
        if commit:
            user.save()
        '''user_registered.send  прочитать instance?? должны
    быть данные переданные '''
        user_registered.send(RegisterUserForm, instance=user)
        return user
    
    class Meta:
        model = UserRegister
        fields = ('username', 'email', 'password1', 'password2', 'first_name',
                  'last_name', 'send_messages')
