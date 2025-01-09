# Create your views here.
from django.shortcuts import render
from rest_framework import (viewsets, generics, mixins)
from rest_framework.response import Response
from django.http import JsonResponse

# from cloud_user.forms import RegisterUserForm
# from cloud_user.forms_more.forms_login import LoginForm
from cloud_user.models import UserRegister
from cloud_user.more_serializers.serializer_update import LoginUpSerializer
from cloud_user.serializers import RegisterUserSerializer
from asgiref.sync import sync_to_async
class RegisterUserView(viewsets.ModelViewSet):
  queryset = UserRegister.objects.all()
  serializer_class = RegisterUserSerializer
  # permission_classes = [IsAdminUser]
  
# class LoginUpViews(viewsets.ModelViewSet ):
class LoginUpViews(generics.RetrieveUpdateAPIView):
  """
  TODO: This the method for user's profile activation.\
      URL for a contact is "api/v1/users/login/<int:pk>"\
      Method: PATCH
      Here, the entrypoint receives data (JSON).
      ```json
      ```
  """
  queryset = UserRegister.objects.all()
  serializer_class = LoginUpSerializer
  #
  
  def patch(self, request, *args, **kwargs):
    if request.method.lower() == "patch":
      data = request.data
      if data:
        for item in data.keys():
          kwargs[item] = data[item]
      if len(kwargs.keys()) >= 1 and len(kwargs.keys()) <= 2:
        super().patch(request, args, kwargs)
        return JsonResponse(status=400)
      elif len(kwargs.keys()) >= 3 and len(kwargs.keys()) <= 4:
        super().patch(request, args, kwargs)
        return JsonResponse({"status": "login"}, status=200)
      return JsonResponse({
        "error":
          f"{LoginUpViews.__class__}.{self.patch.__name__} Mistake => \
Something what wrong"}, status=400)
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

