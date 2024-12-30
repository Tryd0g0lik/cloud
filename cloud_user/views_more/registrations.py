from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

from cloud_user.forms_more.registrations import RegisterUserForm

from cloud_user.models import UserRegister


class RegisterUserView(CreateView):
  model = UserRegister
  template_name = 'users/register_user.html'
  form_class = RegisterUserForm
  success_url = reverse_lazy('accounts:register:register_done')


class RegisterDoneView(TemplateView):
  template_name = 'users/register_done.html'
