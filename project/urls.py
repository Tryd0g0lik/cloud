"""
project/urls.py
URL configuration for project project.

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

from django.contrib import admin

from django.urls import include, path, re_path

from cloud.views import user_update_sessionTime
from cloud_file.urls_files import urlpatterns_files
from cloud_file.views import FileStorageViewSet
from cloud_user import views as vws
# from cloud_user.urls_users import urlpatterns
from cloud_user.urls_users import urlpatterns_user, router2



urlpatterns = [
    path('admin/', admin.site.urls),
    path("", vws.main, name="main"),
    path("users/registration/", vws.main, name="main"),
    path("users/login/", vws.main, name="main"),
    path("profile/<int:pk>/", vws.main, name="main"),
    
    path("api/v1/users/", include((urlpatterns_user, "user"), namespace="user")),
    path("api/v1/users/patch/", include(router2.urls)),
    path("api/v1/files/", include((urlpatterns_files, "files"), namespace="file")),
    path("api/v1/session/increase/time/", user_update_sessionTime, name="session"),
    
    # path('api/v1/users/activate/<str:sign>', user_activate, name="user_activate"),
    # path("api/v1/users/", include((router.urls, "user"), namespace="user")),
]