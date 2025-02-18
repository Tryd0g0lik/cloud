from httpcore import Response
from django.core.cache import cache
from project.settings import (SESSION_COOKIE_HTTPONLY, SESSION_COOKIE_SECURE,
                              SESSION_COOKIE_SAMESITE, SESSION_COOKIE_AGE,
                              SECRET_KEY)


class Cookies:
    def __init__(self, user_id: int, response):
        self.response = response
        self.user_id = user_id
    
    def user_session(
      self,
      max_age_=SESSION_COOKIE_AGE,
      httponly_=True,
      secure_=str(SESSION_COOKIE_SECURE),
      samesite_=SESSION_COOKIE_SAMESITE
      ):
        self.response.set_cookie(
            f"user_session",
            cache.get(
                f"user_session_{self.user_id}"
            ),
            max_age=max_age_,
            httponly=httponly_,
            secure=secure_,
            samesite=samesite_
            )
        return self.response
    
    def is_staff(
      self, is_staff: bool,
      max_age_=SESSION_COOKIE_AGE,
      httponly_=True,
      secure_=str(SESSION_COOKIE_SECURE),
      samesite_=SESSION_COOKIE_SAMESITE
      ):
        self.response.set_cookie(
            f"is_staff",
            is_staff,
            max_age=max_age_,
            httponly=httponly_,
            secure=secure_,
            samesite=samesite_
        )
        return self.response
    
    def is_active(
      self, is_active_: bool,
      max_age_=SESSION_COOKIE_AGE,
      httponly_=SESSION_COOKIE_HTTPONLY,
      secure_=str(SESSION_COOKIE_SECURE),
      samesite_=SESSION_COOKIE_SAMESITE
      ):
        self.response.set_cookie(
            "is_active",
            str(is_active_),
            max_age=max_age_,
            httponly=httponly_,
            secure=secure_,
            samesite=samesite_
        )
        return self.response
    
    def user_index(
      self,
      max_age_=SESSION_COOKIE_AGE,
      httponly_=False,
      secure_=str(SESSION_COOKIE_SECURE),
      samesite_=SESSION_COOKIE_SAMESITE
      ):
        self.response.set_cookie(
            f"index",
            self.user_id,
            max_age=max_age_,
            httponly=httponly_,
            secure=secure_,
            samesite=samesite_
        )
        return self.response
    
    def All(
      self, is_staff: bool,
      is_active: bool
      ):
        self.user_session(self.user_id)
        self.is_staff(is_staff)
        self.is_active(is_active)
        self.user_index(self.user_id)
        return self.response
    
    def empty_templete(
      self, key,
      value,
      max_age_=SESSION_COOKIE_AGE,
      httponly_=False,
      secure_=str(SESSION_COOKIE_SECURE),
      samesite_=SESSION_COOKIE_SAMESITE
      ):
        self.response.set_cookie(
            key,
            value,
            max_age=max_age_,
            httponly=httponly_,
            secure=secure_,
            samesite=samesite_
        )
        
        return self.response