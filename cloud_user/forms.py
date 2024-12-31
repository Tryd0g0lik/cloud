import logging
from django import forms
from cloud_user.models import UserRegister
# from django.utils.translation import gettext_lazy as _
from logs import configure_logging, Logger

configure_logging(logging.INFO)
log = logging.getLogger(__name__)

class CustomRegistrationForm(forms.ModelForm, Logger):
  """
  TODO: Here is registration a new user for site.
  
  """
  class Meta:
    model = UserRegister
    fields = ['username', 'email', 'password']
    log.info("Meta was.")

  def save(self, commit: bool=True):
    __text = f"[{self.print_class_name()}.{self.save.__name__}]:"
    try:
      user = UserRegister()
      user.email = self.cleaned_data['email']
      user.password1 = self.cleaned_data['password1']
  
      if commit:
        __text = f"{__text} New user was registered."
        user.save()
      else:
        __text = f"{__text} New user was not registered/"
      
      return user
    except Exception as e:
      __text = f"{__text} Mistake => {e.__str__()}."
    finally:
      if "Mistake" in __text:
        log.error(__text)
      else:
        log.info(__text)

class CustomAutorisationsForm(forms.Form):
  email = forms.EmailField(label="email", validators=[])
  password = forms.CharField(label="password",
                             widget=forms.PasswordInput,
                             min_length=10, max_length=30)
  