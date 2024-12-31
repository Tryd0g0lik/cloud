from django import forms
from cloud_user.models import UserRegister
# from django.utils.translation import gettext_lazy as _

class CustomRegistrationForm(forms.ModelForm):
  """
  TODO: Here is registration a new user for site.
  
  """
  class Meta:
    model = UserRegister
    fields = ['username', 'email', 'password']

  def save(self, commit=True):
    user = UserRegister()
    user.email = self.cleaned_data['email']
    user.password1 = self.cleaned_data['password1']

    if commit:
      user.save()
    return user

class CustomAutorisationsForm(forms.Form):
  email = forms.EmailField(label="email", validators=[])
  password = forms.CharField(label="password",
                             widget=forms.PasswordInput,
                             min_length=10, max_length=30)
  