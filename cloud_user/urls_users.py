"""
URL router for the 'cloud_user', it is project modul .
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import (path, include)
from rest_framework import routers, urls

from cloud_user.views import RegisterUserView, LoginUpViews

from cloud_user.contribute.controler_activate import user_activate

router = routers.DefaultRouter()
router.register('newuser', RegisterUserView,  basename='newuser')
# router.register('login', LoginUpViews, basename='login')

urlpatterns_user = [
    path('activate/<str:sign>', user_activate, name="user_activate"),
    path('login/<int:pk>', LoginUpViews.as_view(), name="login"),
    path("register/", include(router.urls))
    
]
# , namespace="profile"
