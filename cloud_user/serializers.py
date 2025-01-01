"""Here is a serializer fot user registration"""
import logging
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
# from datetime import datetime
from cloud_user.models import UserRegister
from logs import configure_logging, Logger

configure_logging(logging.INFO)
log = logging.getLogger(__name__)

class RegisterUserSerializer(serializers.ModelSerializer):
    log.info("START")
    class Meta:
        model = UserRegister
        fields = ["id", "email", "send_messages",
                  "is_activated", "is_active",
                  "is_superuser"]
        # log.info("Meta was!")
    
    def create(self, **validated_data):
        """
        TODO: This is a serializer method for a creating of new user in db
        :param validated_data, is confirmed data
        :return UserRegister(validated_data)
        """
        # __text = f"[{self.print_class_name()}.{self.create.__name__}]:"
        __text = f"[{self.create.__name__}]:"
        log.info(f"{__text} START.")
        try:
            new_user = UserRegister(validated_data)
            __text = f"{__text} was crated."
            return new_user.save()
        except Exception as e:
            __text = f"{__text} Mistake => \
{e.__str__()}."
            raise ValueError(__text)
        finally:
            if "Mistake" in __text:
                log.error(__text)
            else:
                log.info(__text)
            log.info("END")
            
    
    
# class Users_serializers(serializers.ModelSerializer):
#     date_joined = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S.855512",
#                                             required=False)
#     username = serializers.CharField(min_length=3,
#                                      max_length=30,
#                                      help_text=_(f"Длина логина не меньше 3 и \
#                                      не больше 30 символов."))
#
#     class Meta:
#         pass
#         model = UserRegister
#         fields = ['id', 'email', 'username', 'password', 'date_joined']
#         extra_kwargs = {'password': {'write_only': True}}
#
#     def validate_username(self, value):
#         username_list = \
#             UserRegister.objects.filter(username__startswith=value)
#
#         if self.context['request'].method == 'POST' and \
#           len(list(username_list)) > 0:
#             raise ValueError(_(f'Пользователь с таким \
# именем {value} уже существует в базе данных!'))
#         if self.context['request'].method == 'PUT':
#             pass
#         return value
#
#     def validated_email(self, value):
#         email_list = \
#             UserRegister.objects.filter(username__startswith=value)
#         if len(list(email_list)) > 0:
#             raise ValueError(_(f'Пользователь с таким email: \
# {value} уже существует в базе данных!'))
#         return value
#
#     def validate_date_joined(self, value):
#         if not value:
#             import datetime
#             value = datetime.datetime.now()
#         return value
#
#     # `self.context['request'].data.get('email')` можно получить данные. Вставить имя формы
#     # ведь post с обоих форм идет на один урл.
#     # авторизация
#     def create(self, validated_data):
#         validated_data['date_joined'] = datetime.now()
#         validated_data['is_active'] = False
#         return super().create(validated_data)
#
#     # https://www.django-rest-framework.org/api-guide/serializers/#saving-instances
#     def update(self, instance, validated_data):
#         email = validated_data.get('email')
#         username = validated_data.get('username')
#         try:
#             if bool(email) and email != instance.email:
#                 raise ValueError(_(f"[{str(datetime.now().time())[:-4]} >> \
#                 update >> email]: A email of user \
# can't changing. Write to support"))
#             if bool(username) and username != instance.username:
#                 raise ValueError(_(f"[{str(datetime.now().time())[:-4]} >> \
#                 update >> username]:A username can't changing. \
# Write to support"))
#         except Exception as er:
#             print(er)
#         instance.password = validated_data.get('password')
#         instance.save()
#
#         return instance
