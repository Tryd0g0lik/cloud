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
from django.urls import (path, include)
from rest_framework import routers, urls

from cloud_user.views import (UserView, UserPatchViews, send_message,
                              csrftoken)

from cloud_user.contribute.controler_activate import user_activate

router = routers.DefaultRouter()
router.register("", UserView, basename="fulluser")
router.register("<int:pk>/", UserView, basename="profileuser")
# router.register("/<str:data>/parameters/", UserPatchViews)
# router.register("login", UserPatchViews, basename="login")
router2 = routers.DefaultRouter()
router2.register("", UserPatchViews, basename="login", )
urlpatterns_user = [
    path("activate/<str:sign>/", user_activate, name="user_activate"),
    path("email/message/", send_message, name="emailmessage"),
    # path("patch/<int:pk>/", UserPatchViews.as_view(), name="login"),
    # path("patch/", include(router2.urls), name="login"),
    # path("parameters/<str:pk>/", UserPatchViews.as_view(), name="parameters"),
    # path("parameters/", UserPatchViews.as_view()),
    # path("/api/v1/users/get/<str:data>/", send_index, name="parameters"),
    path("", csrftoken),
    path("choice/", include(router.urls)),
    # path("change/", include(router2.urls))
    
    
]
# , namespace="profile"
