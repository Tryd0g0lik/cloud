"""
cloud_user/views.py
"""
import scrypt
import json
import logging
from datetime import datetime

from django.contrib.auth.hashers import make_password
from django.shortcuts import render
from django.core.cache import (cache)
from rest_framework import (viewsets, generics, status)
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from cloud_user.tasks import ready, _run_async
from project.settings import (SECRET_KEY, SESSION_COOKIE_AGE, \
                              SESSION_COOKIE_SECURE, SESSION_COOKIE_SAMESITE,
                              SESSION_COOKIE_HTTPONLY)
from django.views.decorators.csrf import get_token
from cloud.services import (get_data_authenticate, decrypt_data)
from cloud_user.apps import signal_user_registered
from cloud_user.contribute.sessions import (check,
                                            hash_create_user_session)
from cloud.hashers import hashpw_password
from cloud_user.models import UserRegister
from cloud_user.more_serializers.serializer_update import UserPatchSerializer
from cloud_user.serializers import UserSerializer
import asyncio
from cloud_user.contribute.services import get_fields_response, get_user_cookie
from logs import configure_logging

configure_logging(logging.INFO)
log = logging.getLogger(__name__)
log.info("START")


async def csrftoken(request):
    if (request.method != "GET"):
        return JsonResponse(status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse(
        {"csrftoken": get_token(request)}, status=status.HTTP_200_OK
        )


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
              cacher.user_session == cache.get(
                f"user_session_{cookie_data.id}"
                ):
                # Below, check, It is the superuser or not.
                # Check, 'user_settion_{id}' secret key from COOCIE is aquils to
                # 'user_settion_{id}' from cacher table of db
                # /* ---------------- cacher.is_superuser = True Удалить ---------------- */
                if cacher.is_superuser == True:
                    # Если администратор, получаем всех пользователей
                    files = UserRegister.objects.all()
                    serializer = UserSerializer(files, many=True)
                    return Response(serializer.data)
                else:
                    files = UserRegister.objects.filter(id=int(cookie_data.id))
                    
                    serializer = UserSerializer(files, many=True)
                    instance = get_fields_response(serializer)
                    return Response(instance)
            res = {"message": f"[{__name__}::list]: "}
            return JsonResponse(data=res)
        except Exception as e:
            return JsonResponse(
                data={"message": f"[{__name__}::list]: \
Mistake => f{e.__str__()}"}
                )
    
    def retrieve(self, request, *args, **kwargs):
        
        user_session = request.COOKIES.get(f"user_session")
        check_bool = check(
            f"user_session_{kwargs['pk']}", user_session, **kwargs
            )
        
        if not check_bool:
            return Response(
                {"message":
                     f"[{__name__}::{self.__class__.retrieve.__name__}]:\
Your profile is not activate"}
                ), 404
        # if 'pk' in kwargs.keys():
        instance = super().retrieve(request, *args, **kwargs)
        instance = get_fields_response(instance)
        return JsonResponse(instance)
        # /* ----------- Вставить прова и распределить логику СУПЕРЮЗЕРА ----------- */
    
    def dispatch(self, request, *args, **kwargs):
        resp = None
        try:
            resp = super().dispatch(request, *args, **kwargs)
            
            # return JsonResponse(resp.data, status=resp.status_code)
            return resp
        except Exception as e:
            return JsonResponse({}, status=400)
    
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
        check_bool = check(
            f"user_session_{kwargs['pk']}", user_session, **kwargs
            )
        
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
        password = json.loads(request.body)["password"]
        password_validation(password)
        hash = hashpw_password(f'pbkdf2${str(20000)}{password}') #.decode("utf-8")
        json.loads(request.body)["password"] = hash
        
        instance = super().update(request, *args, **kwargs)
        return Response(instance.data, status=200)  # Проверить
    
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
        data = request.data
        # password_byte = make_password(data["password"].encode("utf-8"))
        password_byte = data["password"].encode("utf-8")
        # data["password"] = password_byte
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors, status=400)
            # instance = super().create(request, *args, **kwargs)
        """
            def create(self, request, *args, **kwargs):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED,
                headers=headers
                )
                
                create eбопть из насле дия. Пароль сделать  - бинарный!!
        """
        # instance = super().create(request, *args, **kwargs)
        # request.data['password'] = make_password(request.data['password'])
        instance = get_fields_response(serializer)
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
        check_bool = check(
            f"user_session_{kwargs['pk']}", user_session, **kwargs
            )
        
        # CHECK to USER
        class DataCookie:
            pass
        
        # GET user ID
        cookie_data = get_data_authenticate(request)
        cacher = {
            'user_session': cache.get(f"user_session_{cookie_data.id}"),
            'is_superuser': cache.get(f"is_superuser_{cookie_data.id}")
        }
        
        if not check_bool:
            return Response(
                {
                    "message": f"[{__name__}::{self.__class__.destroy.__name__}]: Not OK"}
                )
        try:
            if cacher["is_superuser"] and \
              cacher["user_session"] == cache.get(
                f"user_session_{cookie_data.id}"
                ):
                # Remove the user
                instance = super().destroy(request, *args, **kwargs)
                # Remove cache the user
                cache.delete(f"user_session_{kwargs['pk']}")
                cache.delete(f"is_superuser{kwargs['pk']}")
                instance = Response()
        except Exception as e:
            instance = Response(
                {"message": f"Not Ok.\
Mistake => {e.__str__()}", }, status=400
                )
        finally:
            return instance


# class UserPatchViews(viewsets.ModelViewSet ):
class UserPatchViews(generics.RetrieveUpdateAPIView, viewsets.GenericViewSet):
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
    
    
    @staticmethod
    def update_cell( request, *args, **kwargs):
        """
      For update data of single cell or more cells. \
      If make to change to the databasebase, to inside of the 'update_cell' \
      will send a response to the user client's request. \
      Entry point of the 'update_cell' function will need has a min of \
      the data from: \
      - request.body \
      - kwargs["pk"] \
      Then the 'update_cell' function will perform successfully then, from \
      the 'update_cell' will sending a response to the user client. \
      This the status-code 200 \
      Or, not successfully and will send a response with the status-code 400
      :param request:
      :param args:
      :param kwargs:
      :return:
    """
        # Get data from the reqyest body.
        data = json.loads(request.body)
        user_list = UserRegister.objects.filter(id=kwargs["pk"])
        # CREATE RESPONSE
        if len(data.keys()) > 0:
            kwargs["id"] = (lambda: int(kwargs["pk"]))()
            for item in data.keys():
                if item == "id":
                    continue
                # CHANGE PASSWORD
                if "password" == item and "is_active" not in data.keys():
                    """
                  Hash the password from the data user's request. It's\
                  from the entry-point.
                  """
                    __hash_password = UserPatchViews.hash_password(
                        (lambda: data['password'])()
                        )
                    
                    data[item] = __hash_password
                elif "password" == item and "email" in data.keys() and \
                  "is_active" in data.keys():
                    authenticity = True if data["email"] == user_list[0].email else False
                    if not authenticity:
                        # status code 400
                        response = JsonResponse(
                            {"detail": "Password or email is invalid!"},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                        # GET COOKIE
                        response = get_user_cookie(request, response)
                        return response
                    continue
                
                # next
                kwargs[item] = (lambda: data[item])()
          
            user = user_list[0]
            # CHANGE THE PROPERTY of the user object.
            for item in kwargs.keys():
                if item == "pk" or item == "id":
                    continue
                user.__setattr__(item, kwargs[item])
                user.save(update_fields=[item])
            # CREATE RESPONSE
            instance = UserPatchSerializer(user_list.first(), many=False)
            instance = get_fields_response(instance)
            response = JsonResponse(instance, status=200)
            # IF IS_ACTIVE CHANGE
            if "is_active" in data:
                hash_create_user_session(
                    kwargs['pk'],
                    f"user_session_{kwargs['pk']}"
                )
                hash_create_user_session(
                    kwargs['pk'],
                    f"user_superuser_{kwargs['pk']}"
                )
                if not data["is_active"]:
                    cache.delete(f"user_session_{kwargs['pk']}")
                    cache.delete(f"user_superuser_{kwargs['pk']}")
                if data["is_active"]:
                    kwargs["last_login"] = datetime.utcnow()
           
            # GET the DATA COOKIE
            response = get_user_cookie(request, response)
            return response
        return JsonResponse(
            {"detail": "Something what wrong!"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def options(self, request, *args, **kwargs):
        response = super().options(request, *args, **kwargs)
        return response
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        # return Response(request.body)
        return response
    
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return response
    
    def partial_update(self, request, *args, **kwargs):
        # response = super().partial_update(request, *args, **kwargs)
        response = self.patch_change(request, *args, **kwargs)
        return response
    
    def get(self, request, *args, **kwargs):
        
        response = super().get(request, *args, **kwargs)
        return response
    
    # @csrf_exempt
    
    # @action(detail=True, methods=['patch', 'option'])
    
    def patch(self, request, *args, **kwargs):
        # response = super().patch(request, *args, **kwargs)
        response = self.patch_change(request, *args, **kwargs)
        return response
    
    def patch_change(self, request, *args, **kwargs):
        
        """
    Возвращает данные для COOKIE ('user_session_{id}')  если\
json.loads(request.body)["is_active"] == True, and 'is_active'
     We does can not update the 'is_superuser' property

    :param request:
    :param args:
    :param kwargs:
    :return: the data of body and 'user_session_{id}' from cookie
    """
        
        # cacher.is_superuser = cache.get(f"is_superuser_{kwargs['pk']}")
        try:
            # Get data from the reqyest body.
            data = json.loads(request.body)
            # GETs the cookie's data how an object from the user's ID
            cookie_data = get_data_authenticate(request)
            user_list = UserRegister.objects.filter(id=kwargs["pk"])
            # If we do not have cookie's data, then we look to the password of user.
            if (not hasattr(cookie_data, "user_session") or (
              hasattr(cookie_data, "user_session") and
              not cache.get(f"user_session_{kwargs['pk']}")
            )) and \
              len((data.keys())) > 0:
                
                if len(user_list) == 0:
                    return Response(
                        {"message": f"[{__name__}]: \
Something what wrong. Check the 'pk'."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                # Comparing password of the user
                _hash_password = self.hash_password(
                    (lambda: data["password"])()
                    )
                if user_list[0].password != _hash_password:
                    return Response(
                        {"message": f"[{__name__}]: \
Something what wrong. Check the 'password'."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                """
                If make to change to the database, to inside of the 'update_cell'\
                will send a response to the user client's request.
                """
                body = json.loads(request.body)
                body["password"] = user_list[0].password
                request.body = json.dumps(body)
                response = UserPatchViews.update_cell(request, *args, **kwargs)
                return  response
            cacher = {
                'user_session': cache.get(f"user_session_{kwargs['pk']}"),
            }
            
            
            if cacher['user_session'] and cookie_data.user_session:
                user_session = scrypt.hash(cacher["user_session"], SECRET_KEY)
                if cookie_data.user_session == (user_session).decode(
                  'ISO-8859-1'
                ) and request.method.lower() == "patch":
                    user_session = request.COOKIES.get(f"user_session")
                    # CHECK a COOKIE KEY ?????????????????
                    check_bool = check(
                        f"user_session_{kwargs['pk']}", user_session, **kwargs
                        )
                    if not check_bool:
                        return Response(
                            {"message": f"[{__name__}]: \
    Something what wrong. Check the 'pk'."}
                        )
                    response = UserPatchViews.update_cell(request, *args, **kwargs)
                    return response
            return JsonResponse(
                {"detail": "Something what wrong! \
Check the 'user_session' or 'pk'"},
                status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {
                    "message": "Not Ok",
                    "error":
                        f"{UserPatchViews.__class__}.{self.patch.__name__} Mistake => \
{e.__str__()}"}, status=400
            )
        finally:
            cache.close()
    
    def hash_password(self, password: str, encode='windows-1251'):
        """
    Hash the password from the data user's request.
    Every time we get the one static hash of password if the entry-point get\
     the pure  user's password of static.
    :param password: str. Pure password from user's request.
    :return: str. Hash of password.
    """
        from base64 import b64encode
        # _hash_password = scrypt.hash(f"pbkdf2${str(20000)}${(lambda: password)()}",
        #                 SECRET_KEY).decode(encode)
        _hash_password = scrypt.hash(
            f"pbkdf2${str(20000)}${(lambda: password)()}", SECRET_KEY
        )
        #.replace(r"[ \t\v\r\n\f]+", "") ##.replace("\n", "").replace(r" ", "")
        return b64encode(_hash_password).decode()
    
    def put(self, request, *args, **kwargs):
        json.loads(request.body)["Message"] = "Not Ok"
        return Response(json.loads(request.body), status=400)
    
    # def get_extra_action(self):
    #   return [self.send_index]


@api_view(['GET'])
def api_get_index(request, **kwargs):
    """
  Received the request to restore the index by email of user.\
  URL contein the user of email, but only  the email address is encrypted.\
  The sub-function 'decrypt_data' contain algorithm for decryption.\
  :param request: method GET. URL contain one parameter of email address..
  :param kwargs: empty.
  :return:
  """
    decrypt_data_str = ""
    serializers = {}
    
    try:
        # Пример использования
        secret_key = f"{SECRET_KEY}"  # Убедитесь, что длина ключа соответствует требованиям (16/24/32 байта)
        crypto_data = request.GET.get(
            'data'
            )  # Замените на ваш зашифрованный email
        # Function of DECRYPTion.
        decrypted_data: str = decrypt_data(crypto_data, secret_key)
        decrypt_data_str += decrypted_data
    
    except Exception as e:
        print("Ошибка при расшифровке:", str(e))
    else:
        response = UserRegister.objects.filter(
            email__contains=decrypt_data_str
            )
        if len(response) > 0:
            serializers.update(
                UserPatchSerializer(response[0], many=False).data
                )
        else:
            return JsonResponse(
                {"detail": "Not found"}, status=status.HTTP_400_BAD_REQUEST
            )
    return JsonResponse({"data": serializers["id"]}, status=status.HTTP_200_OK)


def main(request, pk=None):
    if request.method.lower() == "get":
        template = "users/index.html"
        title = "Главная"
        context_ = {"page_name": title}
        response = render(request, template, {})
        # GET COOKIE
        response = get_user_cookie(request, response)
        return response


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
            return password
    
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
    
    # asyncio.create_task((lambda: sync_to_async(UserSerializer.objects.filter)(email=email)))


ready(_run_async)
