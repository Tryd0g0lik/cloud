from django.urls import (path, include)
from rest_framework import routers

from cloud.views import AdminView
from cloud_user.contribute.controler_activate import user_activate

routers = routers.DefaultRouter()
routers.register("", AdminView, basename="admin")
routers.register(r"<int:pk>/remove/", AdminView, basename="admin_user_remove")

urlpatterns_admin = [
    # path("", include(routers.urls)),
    path("activate/<str:sign>/", user_activate, name="admin_activate"),
    path("choice/", include(routers.urls)),
    
]
