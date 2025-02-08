"""
cloud_user/serializers.py
Not more functions
"""
import scrypt
import requests
from cloud_user.models import UserRegister
from django.core.cache import (cache)
from cloud_user.contribute.sessions import (check,
                                            hash_create_user_session)

def find_superuser()-> [object, None]:
    """
    TODO: Checker. It checks, we have a superuser in db or not/
'True' if haves a superuser or 'False'
    :return: object or None
    """
    superuser_list = UserRegister.objects.filter(is_superuser=True)
    if len(superuser_list) > 0:
        return superuser_list[0]
    return None

def get_fields_response(obj,
                        exclude_instance=[]
                        ):
    """
    TODO: This is function for returning the set of fields. They are sending \
in response for the client.
    :param exclude_instance: list. This for the fields exclude. Bu default is \
    ["password", "is_activated",
    "email",  "send_messages",
    "groups", "user_permissions"]
    return \
     ```json
       {
         "id": 19,
         "last_login": null,
         "is_superuser": false,
         "username": "",
         "first_name": "Денис",
         "last_name": "Королев",
         "is_staff": false,
         "is_active": true,
         "date_joined": "2025-01-03T13:01:53.238635+07:00"
       }
     ```
   """
    if len(exclude_instance) == 0:
        exclude_instance = ["password", "is_activated",
                            "email",  "send_messages",
                            "groups", "user_permissions"]
    new_instance = {}
    for k, v in dict(obj.data).items():
        if k in exclude_instance:
            continue
        new_instance[f"{k}"] = v
    # obj.data = new_instance
    return new_instance


def get_user_cookie(request: type(requests),
                    response: type(requests.models.Response),
                    **kwargs) -> type(requests.models.Response):
    """
    From the request we receive an index of user. Then, to the response add the\
    cookie data:
     -'user_session_{index}' from the cacher table's db;
     - 'is_superuser' from the users table's db;
     - 'is_active' from the users table's db.
     The variables above, these data for COOKIES.
    :param request: protocol 'http(s)' methods: 'GET' ... 'PATCH'.
    :param response: for the web client.
    :return:
    """
    from project.settings import (SECRET_KEY, SESSION_COOKIE_AGE, \
                                  SESSION_COOKIE_SECURE,
                                  SESSION_COOKIE_SAMESITE,
                                  SESSION_COOKIE_HTTPONLY)
    user_list = []
    index = request.COOKIES.get("index") if \
        request.COOKIES.get("index") else \
        (kwargs["pk"] if 'pk' in kwargs else None)
        # index = request.COOKIES.get("index")
    if not index:
        import re
        index_list = re.findall(r"\d+", request.path)
        if len(index_list) > 0:
            index = index_list[-1]
    if index != None:
        user_list = UserRegister.objects.filter(id=int(index))
    if len(user_list) > 0:
        # Check the "user_session_{index}", it is in the cacher table or not.
        user_session = cache.get(f"user_session_{index}")
        if user_session == None:
            hash_create_user_session(int(index), f"user_session_{index}")
    if index != None:
        response.set_cookie(
            f"user_session",
            scrypt.hash(
                cache.get(
                    f"user_session_{index}"
                ), SECRET_KEY
            ).decode('ISO-8859-1'),
            max_age=SESSION_COOKIE_AGE,
            httponly=True,
            secure=SESSION_COOKIE_SECURE,
            samesite=SESSION_COOKIE_SAMESITE
        )
        response.set_cookie(
            f"is_superuser",
            user_list[0].is_superuser,
            max_age=SESSION_COOKIE_AGE,
            httponly=SESSION_COOKIE_HTTPONLY,
            secure=SESSION_COOKIE_SECURE,
            samesite=SESSION_COOKIE_SAMESITE
        )
        response.set_cookie(
            f"is_active", user_list[0].is_active,
            max_age=SESSION_COOKIE_AGE,
            httponly=SESSION_COOKIE_HTTPONLY,
            secure=SESSION_COOKIE_SECURE,
            samesite=SESSION_COOKIE_SAMESITE
        )
        response.set_cookie(
            "index", index,
            max_age=SESSION_COOKIE_AGE,
            httponly=SESSION_COOKIE_HTTPONLY,
            secure=SESSION_COOKIE_SECURE,
            samesite=SESSION_COOKIE_SAMESITE
        )
    return response

