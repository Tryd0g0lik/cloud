# Create your views here.
from django.shortcuts import render
from rest_framework import (viewsets, generics, mixins)
from rest_framework.response import Response
from django.http import JsonResponse

# from cloud_user.forms import RegisterUserForm
# from cloud_user.forms_more.forms_login import LoginForm
from cloud_user.models import UserRegister
from cloud_user.more_serializers.serializer_update import UserPatchSerializer
from cloud_user.serializers import RegisterUserSerializer
from asgiref.sync import sync_to_async
class RegisterUserView(viewsets.ModelViewSet):
  queryset = UserRegister.objects.all()
  serializer_class = RegisterUserSerializer
  # permission_classes = [IsAdminUser]
  
# class UserPatchViews(viewsets.ModelViewSet ):
class UserPatchViews(generics.RetrieveUpdateAPIView):
  """
  TODO: For update data of single cell or more cells.
    Method: PATCH.
    URL: for a contact is "api/v1/users/patch/<int:pk>"
    Method: PUT is not works.
  :return \
    ```json
    {
      "id": 20,
      "last_login": null,
      "is_superuser": false,
      "username": "Rabbit",
      "first_name": "Денис",
      "last_name": "Сергеевич",
      "is_staff": false,
      "is_active": false,
      "date_joined": "2025-01-08T16:47:53.883666+07:00"
    }
    '''
  """
  queryset = UserRegister.objects.all()
  serializer_class = UserPatchSerializer
  #
  
  def patch(self, request, *args, **kwargs):
    if request.method.lower() == "patch":
      data = request.data
      if data:
        for item in data.keys():
          if item == "id":
            continue
          kwargs[item] = data[item]
        instance = super().patch(request, args, kwargs)
        return Response(instance.data, status=200)
      return Response({
        "message": "Not Ok",
        "error":
          f"{UserPatchViews.__class__}.{self.patch.__name__} Mistake => \
Something what wrong"}, status=400)

  def put(self, request, *args, **kwargs):
    request.data["Message"] = "Not Ok"
    return Response(request.data, status=400)
    # if not validated_data.get("id") or \
    #   not validated_data["is_active"]:
    #   return object()
    # index = validated_data.get("id", instance.id)
    #
    # if not index:
    #   return object()
    # resp_list = UserRegister.objects.filter(id=index)
    # if len(resp_list) == 0:
    #   return object()
    # resp_obj = resp_list.first()
    # resp_obj["is_active"] = validated_data["is_active"]
    # resp_obj.save()
    # return instance

def main(request):
  if request.method.lower() == "get":
    template = "users/index.html"
    title = "Главная"
    context_ = {"page_name": title}
    # if request.path == "register/":
    #   title = "Регистрация"
    #   form = RegisterUserForm()
    #   context_ = {"form": form, "page_name": title}
    # elif request.path == "login/":
    #   title = "Активизация"
    #   form = LoginForm()
    #   context_ = {"form": form, "page_name": title}
    return render(request, template, context_)

