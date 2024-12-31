from django.shortcuts import render
# Create your views here.

from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from cloud_user.forms_more.user_registration import UsersRegistrationForm
from cloud_user.models import UserRegister


class RegisterUserView(CreateView):
  model = UserRegister
  template_name = 'users/index.html'
  form_class = UsersRegistrationForm
  # success_url = reverse_lazy('accounts:register:register_done')
  


class RegisterDoneView(TemplateView):
  template_name = 'users/register_done.html'
