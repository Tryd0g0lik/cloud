"""
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

# from cloud_user.urls_users import urlpatterns
from cloud_user.urls_users import urlpatterns_user




urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/v1/users/", include((urlpatterns_user, "user"), namespace="user")),
    # path('api/v1/users/activate/<str:sign>', user_activate, name="user_activate"),
    # path("api/v1/users/", include((router.urls, "user"), namespace="user")),
]