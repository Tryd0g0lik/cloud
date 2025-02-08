import asyncio
import threading
from copy import copy
from datetime import datetime, timedelta, timezone
from asgiref.sync import async_to_sync, sync_to_async
from django.core.cache import (cache, caches)
import logging
from cloud_user.contribute.hash import Hash
from logs import configure_logging

configure_logging(logging.INFO)
log = logging.getLogger(__name__)
log.info("START")

async def task_check_keys(quantity=0,
                          number=60,
                          range_=1800,
                          hash_live_time=86400):
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
    from cloud_user.models import UserRegister
    # Get the total number of lines from the database
    runs = True
    try:
        # pass
        total_list = await sync_to_async(list)(
            UserRegister.objects.filter(id__gte=0)
        )
        
        # det the total number of lines from the database
        total_quantity = copy(len(total_list))
        total_list.clear()
        while runs:
            if quantity >= total_quantity:
                runs = False
            # Get the list where more when quantity  and less when
            # quantity + number and 'last_login' less when \
            # the now time + range_ seconds
            users = await sync_to_async(list)(
                UserRegister.objects.filter(id__gt=quantity).filter(
                    id__lte=quantity + 60
                ).filter(last_login__lte=(timezone.now() + timedelta(seconds=range_) - timedelta(seconds=hash_live_time)))
            )
            log.info(f'[{task_check_keys.__name__}]: Before update the database \
table "caher" he is the cache')
            for user in users:
                user_id = user.id
                user_session_key = f"user_session_{user_id}"
                user_is_superuser_key = f"user_is_superuser_{user_id}"
                cache.delete(user_session_key)
                cache.delete(user_is_superuser_key)
                if not user.is_active:
                    continue
                
                hash = Hash()
                await hash.set_session_hash(user_session_key, user_id)
            log.info(f'[{task_check_keys.__name__}]: The is completed the cycle.\
Quantity: {quantity}')
            quantity += number
            print(quantity)
    except Exception as e:
        log.error(
            f'[{task_check_keys.__name__}]:\
Mistake => {e.__str__()}'
        )
    finally:
        # self.__cache.close()
        await asyncio.sleep(range_)
        await task_check_keys()
        log.info(f'[{task_check_keys.__name__}]: The end of the cycle')


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
    
