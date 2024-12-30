# from django.urls import path, re_path

from django.urls import path, re_path

from cloud_user.views_more.registrations import RegisterDoneView

RegisterDoneView


urlpatterns = [
        # path('activate/<str:sign>/', user_activate,
        #      name='register_activate'),
        # path('', RegisterUserView.as_view(), name='register'),
        re_path(r'^done/', RegisterDoneView.as_view(),
                name='register_done'),
]