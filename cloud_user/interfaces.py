from django.contrib.auth.backends import BaseBackend
from django.shortcuts import redirect

from cloud.models import UserRegister


class CustomAuthBackend(BaseBackend):
		'''
			TODO: Переопределяем default авторизацию на самописную модель
		'''
		def authenticate(self, request, kwargs=None) -> [list, bool]:
				
				try:
						user_obj_list = UserRegister.objects.filter(id = kwargs['id'] )
						
						if len(list(user_obj_list)) <= 0:
								return False
						
						return user_obj_list
				except Exception as e:
						print(f'[authenticate]: Error {e}')
						return False
				
		def get_user(self, user_id):
				try:
						user = list( UserRegister.objects.filter( pk = user_id ) )
						if len(user) <= 0:
								return False
						return  user[0]
				
				except Exception as e:
					print( f'[authenticate]: Error {e}' )
					return False
				
				
