from django.urls import path, re_path, include

from cloud_user.routers import router_register

# from account.contribute.controler_delete import DeleteUserView
# from account.contribute.vews_changes_profile.interface_forPassword import \
#         APasswordChangeView
# from account.contribute.vews.other_page import account_other_page
# from account.contribute.vews.template_authorizator import \
#         get_form_authorization
# from account.contribute.vews.template_registretor import get_registration
# from account.contribute.vews_changes_profile.intarface_forUser_data import \
#         ChangeInfoView
# from account.views import ALoginView, profile, ALogoutView


urlpatterns = [
        # path('', get_form_authorization, name='accounts'),
        # re_path(r'^form/', get_form_authorization, name='form'),
        # re_path(r'profile/', profile, name='profile'),
        # re_path(r'^profile/change/', ChangeInfoView.as_view(),
        #         name='profile_change'),
        # re_path(r'^profile/delete/', DeleteUserView.as_view(),
        #         name='profile_delete'),
        # re_path(r'^password/change/', APasswordChangeView.as_view(),
        #         name='password_change'),
        # re_path(r'^login/', ALoginView.as_view(), name="login"),
        # re_path(r'^logout/', ALogoutView.as_view(), name='logout'),
        # re_path(r'^registration/', get_registration, name='registration'),
        re_path(r'^register/', include((router_register.urlpatterns,
                                        'register'), namespace='register')),
        # path('<str:page>/', account_other_page, name='accountOther')
]
