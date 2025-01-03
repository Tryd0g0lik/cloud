# Create your views here.
from rest_framework import viewsets

from cloud_user.models import UserRegister
from cloud_user.serializers import RegisterUserSerializer

class RegisterUserView(viewsets.ModelViewSet):
  queryset = UserRegister.objects.all()
  serializer_class = RegisterUserSerializer
  # permission_classes = [IsAdminUser]

