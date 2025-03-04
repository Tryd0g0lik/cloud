"""
cloud_user/serializers.py
Not more functions
"""
import re

import requests
from django.core.cache import cache

from cloud_user.contribute.sessions import hash_create_user_session
from cloud_user.models import UserRegister
from project.settings import (SESSION_COOKIE_AGE, SESSION_COOKIE_HTTPONLY,
                              SESSION_COOKIE_SAMESITE, SESSION_COOKIE_SECURE)


def find_superuser() -> [object, None]:
    """
        TODO: Checker. It checks, we have a superuser in db or not/
    'True' if haves a superuser or 'False'
        :return: object or None
    """
    superuser_list = UserRegister.objects.filter(is_superuser=True)
    if len(superuser_list) > 0:
        return superuser_list[0]
    return None


def get_user_cookie(
  request: type(requests), response: type(requests.models.Response), **kwargs
) -> type(requests.models.Response):
    """
    From the request we receive an index of user. Then, to the response add the\
    cookie data:
     -'user_session_{index}' from the cacher table's db;
     - 'is_staff' from the users table's db;
     - 'is_active' from the users table's db.
     The variables above, these data for COOKIES.
    :param request: protocol 'http(s)' methods: 'GET' ... 'PATCH'.
    :param response: for the web client.
    :return:
    """
    user_list = []
    index = (
        request.COOKIES.get("index")
        if request.COOKIES.get("index")
        else (kwargs["pk"] if "pk" in kwargs else None)
    )
    # index = request.COOKIES.get("index")
    if not index:

        index_list = re.findall(r"\d+", request.path)
        if len(index_list) > 0:
            index = index_list[-1]
    if index:
        user_list = UserRegister.objects.filter(id=int(index))
    if len(user_list) > 0:
        # Check the "user_session_{index}", it is in the cacher table or not.
        user_session = cache.get(f"user_session_{index}")
        if not user_session:
            hash_create_user_session(int(index), f"user_session_{index}")
    if not index:
        # OLD of VERSION S
        response.set_cookie(
            "user_session",
            cache.get(f"user_session_{index}"),
            # scrypt.hash(
            #     cache.get(
            #         f"user_session_{index}"
            #     ), SECRET_KEY
            # ).decode('ISO-8859-1'),
            max_age=SESSION_COOKIE_AGE,
            httponly=True,
            secure=SESSION_COOKIE_SECURE,
            samesite=SESSION_COOKIE_SAMESITE,
        )
        response.set_cookie(
            "is_staff",
            user_list[0].is_staff,
            max_age=SESSION_COOKIE_AGE,
            httponly=SESSION_COOKIE_HTTPONLY,
            secure=SESSION_COOKIE_SECURE,
            samesite=SESSION_COOKIE_SAMESITE,
        )
        response.set_cookie(
            "is_active",
            user_list[0].is_active,
            max_age=SESSION_COOKIE_AGE,
            httponly=SESSION_COOKIE_HTTPONLY,
            secure=SESSION_COOKIE_SECURE,
            samesite=SESSION_COOKIE_SAMESITE,
        )
        response.set_cookie(
            "index",
            index,
            max_age=SESSION_COOKIE_AGE,
            httponly=SESSION_COOKIE_HTTPONLY,
            secure=SESSION_COOKIE_SECURE,
            samesite=SESSION_COOKIE_SAMESITE,
        )
    return response
