from django.shortcuts import render
# Create your views here.

from django.views.generic.base import TemplateView
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from cloud_user.models import UserRegister
from cloud_user.serializers import RegisterUserSerializer


# class RegisterUserView(CreateView):
#   model = UserRegister
#   template_name = 'users/index.html'
#   form_class = UsersRegistrationForm
#   # success_url = reverse_lazy('accounts:register:register_done')

class RegisterUserView(viewsets.ModelViewSet):
  queryset = UserRegister.objects.all()
  serializer_class = RegisterUserSerializer
  # permission_classes = [IsAdminUser]


# class RegisterDoneView(TemplateView):
#   template_name = 'users/register_done.html'
