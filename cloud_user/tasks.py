"""
cloud_user/tasks.py
"""

import asyncio
import logging
import threading
from datetime import timedelta

from asgiref.sync import sync_to_async
from django.core.cache import cache
from django.utils import timezone

from cloud_user.contribute.hashs import Hash
from cloud_user.models import UserRegister
from logs import configure_logging

configure_logging(logging.INFO)
log = logging.getLogger(__name__)
log.info("START")


"""
TASK
"""


async def process_users(users_list_filter, quantity):
    for user in users_list_filter:
        user_id = user.id
        user_session_key = f"user_session_{user_id}"
        # user_superuser_key = f"user_superuser_{user_id}"
        log.info(f"[{process_users.__name__}]: STAR")
        # OLD KEY DELETE
        await sync_to_async(cache.delete)(user_session_key)
        # await sync_to_async(cache.delete)(user_superuser_key)
        log.info(f"[{process_users.__name__}]: The old  linea was removed")
        if not user.is_active:
            continue
        hash_instance = Hash()
        log.info(f"[{process_users.__name__}]: Create the TASK0")
        # NEW KEY MAKE
        await asyncio.gather(
            hash_instance.set_session_hash(user_session_key, user_id),
            # hash_instance.set_session_hash(user_superuser_key, user_id)
        )
        log.info(f"[{process_users.__name__}]: Create the TASK1")
        log.info(
            f"[{process_users.__name__}]: The is completed the cycle.\
Quantity: {quantity}"
        )


@sync_to_async
def get_users(q: int, n: int) -> [object]:
    total_list = list(
        UserRegister.objects.filter(id__gte=q).filter(id__lte=n).filter(is_active=True)
    )

    return total_list


async def task_check_keys(
    quantity=0, number=60, range_=10 * 60 * 60, hash_live_time=86400
):  # 1800
    """
    This is the Task, for check the live time of the line from \
    the 'cache' (it is 'cacher' from 'settings.py').
    Selects the users by ID from the 'quantity' before the 'number' and \
    checking the live time. After, changes the live time for user where \
    the 'last_login' (from the 'UserRegister' model) less when the 'hash_live_time'
    :param quantity: This is the user id for start. For start is 0 and then \
    more and more which the function is working in cycle.
    :param number: This is the total quantity of the range to the ID (users)
    :param range_: This is quantity seconds for restart a function.
    :param hash_live_time: This is the total live time for the hash's line.
    :return:
    """
    # Get the total number of lines from the database
    runs = True
    try:
        while runs:
            object_last_id = await sync_to_async(UserRegister.objects.latest)("id")
            if quantity >= object_last_id.id:
                runs = False
            # Get the list where more when quantity  and less when
            # quantity + number
            users_list = await get_users(quantity, quantity + number)
            log.info(f"[{task_check_keys.__name__}]: users_list: {users_list}")
            users_list_filter = [
                user
                for user in users_list
                if timezone.now() + timedelta(seconds=range_) - user.last_login
                >= timedelta(seconds=(24 * 60 * 60))
            ]
            log.info(
                f'[{task_check_keys.__name__}]: Before update the database \
table "caher" he is the cache. "users_list_filter" Length: \
{len(users_list_filter)}'
            )
            if len(users_list_filter) > 0:
                await process_users(users_list_filter, quantity)
            else:
                pass
                """
                если раскомментировать , надо добавлять проверку хеша -
                а вдруг ДО это был создан хеш.
                Без проверки , ориентируясь на таблицу юзера он протсо по куру  -удалит -создаст
                """
            quantity += number
            # print(quantity)
    except Exception as e:
        log.error(
            f"[{task_check_keys.__name__}]:\
 Mistake => {e.__str__()}"
        )
    finally:
        # self.__cache.close()
        quantity = 0
        await asyncio.sleep(range_)
        await task_check_keys(quantity)
        log.info(f"[{task_check_keys.__name__}]: The end of the cycle")


def _run_async():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(task_check_keys())


def ready(run_async_ofTask):
    log.info(f"{__name__} Hash WAS STARTED")

    # Создаем и запускаем отдельный поток для асинхронных операций
    thread = threading.Thread(target=run_async_ofTask)
    thread.daemon = True  # Демонизированный поток
    thread.start()
