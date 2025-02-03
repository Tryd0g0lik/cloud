import re
import asyncio
from copy import copy
from datetime import (datetime, timedelta)

from asgiref.sync import async_to_sync, sync_to_async
from cloud_user.contribute.sessions import hash_create_user_session
from cloud_user.models import UserRegister
from django.core.cache import (cache, caches)

class Hash:
    def __init__(self, user_id: int | str | None = None):
        """
        :param live_time: int. It is the live time of the session hash. \
        Default the value is 86400.
        :param user_id:
        """
        self.__user_id = user_id
        self.__cache = cache
        self.__user_session = None
        self.__everyone_hash: list[str] = []
        self.__everyone_keys = None
        self.live_time: int = 86400
        # self.__second_hash = None
        # self.user_register = UserRegister.objects.get(user_id=self.user_id)
        # self.user_register_id = self.user_register.id
        # self.user_register_hash = self.user_register.hash
        # self.user_register_hash_id = self.user_register.hash_id
        # self.user_register_hash_id_list = self.user_register_hash_id.split(',')
        # self.user_register_hash_id_list_len = len(self.user_register
    
    async def get_session_hash(self, session_key:  str | None) -> str:
        """
        This method is used to get the one session hash from everything.
        :param session_key: str. It is the session key from the \
'self.__cacher' database. Default the value is "user_session_99993". \
It is the key name. We can indicate the user_id to the method '__init__' \
to the beginning of run the Hash's class of indicate full name \
the 'session_key'. It is the 'get_session_hash' method, irself.
        :return: str | None. It is the session user's hash. Default the value \
is None.
        """
        try:
            if not session_key:
                user_id = self.__user_id if self.__user_id else "99993"
                session_key = f"user_session_{user_id}"
            self.__user_session = self.__cache.get(session_key.split())
        except Exception as e:
            print(
                f'[{Hash.__class__.get_session_hash.__name__}]:\
            Mistake => {e.__str__()}'
                )
        finally:
            return self.__user_session
    
    async def set_session_hash(self, session_key: str,
                               user_id: int | str | None = None,):
        """
        This method is used to set the one session hash to the database.
        :param session_key: str. It is the session key from the \
'self.__cacher' database. Default the value is "user_session_{id}". \
It is the key name.
        :param user_id: str | int | None. It is the user id from of the user \
who is trying to get the session hash.This is from the 'UserRegister'. \
Default the values is None. \
database model.
        
        :return:
        """
        try:
            user_id = user_id if user_id else self.__user_id
            hash_create_user_session(user_id, session_key, copy(self.live_time))
        except Exception as e:
            print(f'[{Hash.__class__.set_session_hash.__name__}]:\
Mistake => {e.__str__()}')


    # @sync_to_async
    
            #     users = UserRegister.objects.filter(
            #         last_login__lte=datetime.utcnow() - timedelta(
            #             seconds=copy(self.live_time - 1800)
            #         )
            #     )
            #     if len(list(users)) == 0:
            #         pass
            #     for user_obj in users:
            #         user_id = user_obj.id
            #         user_session_key = f"user_session_{user_id}"
            #         user_is_superuser_key = f"user_is_superuser_{user_id}"
            #         self.__cache.delete(user_session_key)
            #         self.__cache.delete(user_is_superuser_key)
            #         if user_obj.is_active == False:
            #             continue
            #         loop = asyncio.new_event_loop()
            #
            #         # fut = loop.create_future()
            #         # asyncio.set_event_loop(loop)
            #         def corutin(user_session_key, user_id):
            #             return self.set_session_hash(user_session_key, user_id)
            #
            #         async def update():
            #             loop = asyncio.get_event_loop()
            #             task1 = loop.create_task(corutin(user_session_key, user_id))
            #             task2 = loop.create_task(corutin(user_is_superuser_key, user_id))
            #             await asyncio.gather(task1, task2)
            #
            #         loop.run_until_complete(update())
                    # self.set_session_hash(user_session_key, user_id)
                    # self.set_session_hash(user_is_superuser_key, user_id)
        
                # quantity += number
        except Exception as e:
            print(f'[{Hash.check_keys.__name__}]:\
Mistake => {e.__str__()}')
        finally:
            self.__cache.close()
            # await asyncio.sleep(15)
            # await self.check_keys()
            print('The end of the cycle')
  

    
        
    
