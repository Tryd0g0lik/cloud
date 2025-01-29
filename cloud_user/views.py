"""
cloud_user/views.py
"""
# Create your views here.
import scrypt;
import json
from django.shortcuts import render
from django.core.cache import (cache)
from rest_framework import (viewsets, generics, status)
from rest_framework.response import Response
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.http import JsonResponse
# from django.middleware.csrf import get_token
from project.settings import SECRET_KEY
from django.views.decorators.csrf import get_token, csrf_exempt
from cloud.services import get_data_authenticate
from cloud_user.apps import signal_user_registered
from cloud_user.contribute.sessions import (check,
                                            hash_create_user_session)
from cloud.hashers import hash_password
from cloud_user.models import UserRegister
from cloud_user.more_serializers.serializer_update import UserPatchSerializer
from cloud_user.serializers import UserSerializer

from cloud_user.contribute.services import get_fields_response

async def csrftoken(request):
  if (request.method != "GET"):
    return JsonResponse(status=status.HTTP_400_BAD_REQUEST)
  return JsonResponse({"csrftoken": get_token(request)}, status=status.HTTP_200_OK)
class UserView(viewsets.ModelViewSet):
  """
  TODO: This is complete of REST API, only here is not contain the PATCH method.\
METHOD: GET, CREATE, PUT, DELETE.
  
  """
  queryset = UserRegister.objects.all()
  serializer_class = UserSerializer
  # permission_classes = [permissions.IsAuthenticated]
  # permission_classes = [IsAdminUser]
  
  def options(self, request, *args, **kwargs):
    response = super().options(request, *args, **kwargs)
    return response
  
  def list(self, request, *args, **kwargs):
    # key_list = request.COOKIES.keys()
    # user_session_key_list = \
    #   [key for key in list(key_list) if r"user_session_*" in key]
    # numb = user_session_key_list[0].split("_")[-1]
    # user_session = request.COOKIES.get(f"user_session_{numb}")
    # is_superuser = request.COOKIES.get(f"is_superuser_{numb}")
    class DataCookie:
      pass

    # GET user ID
    cookie_data = get_data_authenticate(request)
    cacher = DataCookie()
    cacher.user_session = cache.get(f"user_session_{cookie_data.id}")
    cacher.is_superuser = cache.get(f"is_superuser_{cookie_data.id}")
    try:
      # Check presences the 'user_session', 'is_superuser' in cacher table of db
      if cacher.is_superuser is not None and \
        cacher.user_session is not None and \
        cacher.user_session == cache.get(f"user_session_{cookie_data.id}"):
        # Below, check, It is the superuser or not.
        # Check, 'user_settion_{id}' secret key from COOCKIE is aquils to
        # 'user_settion_{id}' from cacher table of db
        # /* ---------------- cacher.is_superuser = True Удалить ---------------- */
        if  cacher.is_superuser == True:
          # Если администратор, получаем всех пользователей
          files = UserRegister.objects.all()
          serializer = UserSerializer(files, many=True)
          return Response(serializer.data)
        else:
          # Получаем файлы только текущего пользователя
          files = UserRegister.objects.filter(id=int(cookie_data.id))
      
          serializer = UserSerializer(files, many=True)
          instance = get_fields_response(serializer)
          return Response(instance)
      res = {"message": f"[{__name__}::list]: "}
      return JsonResponse(data=res)
    except Exception as e:
      return JsonResponse(data={"message": f"[{__name__}::list]: \
Mistake => f{e.__str__()}"})
  
  def retrieve(self, request, *args, **kwargs):
   
    user_session = request.COOKIES.get(f"user_session_{kwargs['pk']}")
    check_bool = check(f"user_session_{kwargs['pk']}", user_session, **kwargs)
    
    if not check_bool:
      return Response({"message":
                         f"[{__name__}::{self.__class__.retrieve.__name__}]:\
Your profile is not activate"}), 404
    # if 'pk' in kwargs.keys():
    instance = super().retrieve(request, *args, **kwargs)
    instance = get_fields_response(instance)
    return JsonResponse(instance)
    # /* ----------- Вставить прова и распределить логику СУПЕРЮЗЕРА ----------- */
  
  def dispatch(self, request, *args, **kwargs):
    try:
      resp = super().dispatch( request, *args, **kwargs)
      
      # return JsonResponse(resp.data, status=resp.status_code)
      return resp
    except Exception as e:
      return JsonResponse(resp.content, status=200)
    
  
  def update(self, request, *args, **kwargs):
    """
     We can not update the 'is_superuser' property.
    'request.data["is_superuser"]' the oll time is False
    :param request:
    :param args:
    :param kwargs:
    :return:
    """
    user_session = request.COOKIES.get(f"user_session_{kwargs['pk']}")
    check_bool = check(f"user_session_{kwargs['pk']}", user_session, **kwargs)
    
    # We does can not update the 'is_superuser' property
    if json.loads(request.body)["is_superuser"]:
      json.loads(request.body)["is_superuser"] = False

    if not check_bool:
      return Response(
        {
          "message": f"[{__name__}::{self.__class__.retrieve.__name__}]: \
Your profile is not activate"}
        ), 404
    if json.loads(request.body)["is_superuser"]:
      del json.loads(request.body)["is_superuser"]
      
        # data[item] = f"pbkdf2${str(20000)}{hash.decode('utf-8')}"
    json.loads(request.body)["password"] = \
      f'pbkdf2${str(20000)}{hash_password(json.loads(request.body)["password"]).decode("utf-8")}'
    
    instance = super().update(request, *args, **kwargs)
    return Response(instance.data, status=200) # Проверить
  
  def create(self, request, *args, **kwargs):
    """
    TODO: Entrypoint for the POST method of request \
    '''json
      {
      "last_login": "2024-01-01",
      "password": "ds2Rssa8%sa",
      "email":"user@email.here",
      "is_superuser": false,
      "username": "Victorovich",
      "first_name": null,
      "last_name": "Denis",
      "is_staff": false,
      "is_active": false,
      "date_joined": "2024-01-01"
    }
    '''
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
    :param request:
    :param args:
    :param kwargs:
    :return:
    """
    # data = json.loads(request.body)
    # # /* -----------------временно HASH---------------Перенес в cloud_user/serializers.py-- */
    # hash = hash_password(data["password"])
    # data["password"] = f"pbkdf2${str(20000)}{hash.decode('utf-8')}"
    
    instance = super().create(request, *args, **kwargs)
    instance = get_fields_response(instance)
    response = JsonResponse(data=instance, status=200)
    
    return response
  
  def destroy(self, request, *args, **kwargs):
    """
    TODO: profile user can self remove
    :param request:
    :param args:
    :param kwargs: Contain 'pk' property.
    :return:
    """
    instance = None
    user_session = request.COOKIES.get(f"user_session_{kwargs['pk']}")
    check_bool = check(f"user_session_{kwargs['pk']}", user_session, **kwargs)

    # CHECK to USER
    class DataCookie:
      pass

    # GET user ID
    cookie_data = get_data_authenticate(request)
    cacher = DataCookie()
    cacher.user_session = cache.get(f"user_session_{cookie_data.id}")
    cacher.is_superuser = cache.get(f"is_superuser_{cookie_data.id}")
    
    if not check_bool:
      return Response({"message": f"[{__name__}::{self.__class__.destroy.__name__}]: Not OK"})
    try:
      if cacher.is_superuser and \
        cacher.user_session == cache.get(f"user_session_{cookie_data.id}"):
        # Remove the user
        instance = super().destroy(request, *args, **kwargs)
        # Remove cache the user
        cache.delete(f"user_session_{kwargs['pk']}")
        cache.delete(f"is_superuser{kwargs['pk']}")
        instance = Response()
    except Exception as e:
      instance = Response({"message": f"Not Ok.\
Mistake => {e.__str__()}", }, status=400)
    finally:
      return instance
      
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
  
  
  def options(self, request, *args, **kwargs):
    response = super().options(request, *args, **kwargs)
    return response
  
  # @csrf_exempt
  def patch(self, request, *args, **kwargs):
    """
    Возвращает данные для COOKIE ('user_session_{id}')  если\
json.loads(request.body)["is_active"] == True, and 'is_active'
     We does can not update the 'is_superuser' property

    :param request:
    :param args:
    :param kwargs:
    :return: the data of body and 'user_session_{id}' from cookie
    """
 
    # CHECK to USER
    class DataCookie:
      pass

    # GET user ID
    cookie_data = get_data_authenticate(request)
    cacher = DataCookie()
    cacher.user_session = cache.get(f"user_session_{kwargs['pk']}")
    # cacher.is_superuser = cache.get(f"is_superuser_{kwargs['pk']}")
    try:
      user_session = scrypt.hash(cacher.user_session, SECRET_KEY)
      if cookie_data.user_session == str(user_session) and \
        request.method.lower() == "patch":
        data = json.loads(request.body)
        user_session = request.COOKIES.get(f"user_session")
        # CHECK a COOKIE KEY
        check_bool = check(f"user_session_{kwargs['pk']}", user_session, **kwargs)
        if not check_bool:
            return Response(
              {"message": f"[{__name__}]: \
Something what wrong. Check the 'pk'."}
              )
        
        # /* -------------- Remove 'is_superuser' -------------- */
        if "is_superuser" in data.keys():
          del data["is_superuser"]
          
        user_list = UserRegister.objects.filter(id=kwargs["pk"])
        # CREATE RESPONSE
        if len(data.keys()) > 0:
          kwargs["id"] = int(kwargs["pk"])
          for item in data.keys():
            if item == "id":
              continue
          # CHANGE PASSWORD
          if "password" == item:
            hash = hash_password(data[item])
            data[item] = f"pbkdf2${str(20000)}{hash.decode('utf-8')}"
          kwargs[item] = data[item]
          # CHANGE
          instance = super().patch(request, args, kwargs)
      
          response = Response(instance.data, status=200)
          # CHANGE IS_ACTIVE
          if "is_active" in data:
            hash_create_user_session(kwargs['pk'],
                                     f"user_session_{kwargs['pk']}")
            # (user_list.first()).is_active = True
            # GET NEW value for the cookie's user_session_{id}.
            # response.set_cookie(f"user_session_{kwargs['pk']}", True)
          # elif not data["is_active"]:
          #   (user_list.first()).is_active = False
          user_list.first().save()
        
          return response
        return JsonResponse({"detail": "Something what wrong!"},
                            status=status.HTTP_400_BAD_REQUEST)
      return JsonResponse({"detail": "Something what wrong! \
Check the 'user_session' or 'pk'"},
                          status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
      return Response({
        "message": "Not Ok",
        "error":
          f"{UserPatchViews.__class__}.{self.patch.__name__} Mistake => \
Something what wrong"}, status=400)
    finally:
      cache.close()

  def put(self, request, *args, **kwargs):
    json.loads(request.body)["Message"] = "Not Ok"
    return Response(json.loads(request.body), status=400)

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
    # return render(request, template, context_)
    return render(request, template, {})

def send_message(request):
  data = json.loads(request.body)
  def _clean_password(request):
      password = _clean(request)
      if password:
          password_validation.validate_password(password)
      return password
#
  def _clean(request):
      data = json.loads(request.body)
      password = data['password']
      if password_validation and password:
      
        errors = {'password2': ValidationError(
            'Введенные пароли не \
совпадают', code='password_mismatch'
            )}
        raise ValidationError(errors)
      else:
        return  password
  user = UserRegister()
  user.password = _clean_password(request)
  user.last_login = data["last_login"]
  user.is_superuser = data["is_superuser"]
  user.username = data["username"]
  user.first_name = data["first_name"]
  user.last_name = data["last_name"]
  user.is_staff = data["is_staff"]
  user.is_active = False
  user.date_joined = data["date_joined"]
  user.save()
  
  del data["username"]
  del data["last_login"]
  del data["last_name"]
  del data["is_staff"]
  del data["is_active"]
  del data["date_joined"]
  del data["password"]
  signal_user_registered.send(data, instance=user)
  