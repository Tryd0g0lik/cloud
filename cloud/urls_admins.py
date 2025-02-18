from django.urls import (path, include)
from rest_framework import routers

from cloud.views import AdminView

routers = routers.DefaultRouter()
routers.register("", AdminView, basename="admin")
routers.register(r"<int:pk>/", AdminView, basename="admin_pk")

urlpatterns_admins = [

]