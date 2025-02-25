"""
cloud_user/urls_users.py
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

from django.urls import include, path
from rest_framework import routers

from cloud_user.contribute.controler_activate import user_activate
from cloud_user.views import (UserPatchViews, UserView, api_get_index,
                              csrftoken, send_message)

router = routers.DefaultRouter()
router.register("", UserView, basename="fulluser")
router.register("<int:pk>/", UserView, basename="profileuser")
router2 = routers.DefaultRouter()
router2.register(
    "",
    UserPatchViews,
    basename="login",
)
router2.register(
    "<int:pk>/",
    UserPatchViews,
    basename="login_patch",
)

urlpatterns_user = [
    path("activate/<str:sign>/", user_activate, name="user_activate"),
    path("email/message/", send_message, name="emailmessage"),
    path("", csrftoken),
    path("choice/name/", api_get_index),
    path("choice/", include(router.urls)),
    path("patch/", include(router2.urls)),
]
# , namespace="profile"
