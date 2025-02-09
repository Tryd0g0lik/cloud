"""
cloud_user/contribute/sessions.py
    HASH for work with the cacher (from session) table of db.
    Look to the settings.py::CACHES
 """
import bcrypt

import logging
from django.core.signing import Signer
from django.core.cache import cache
from cloud.hashers import hashpw_password
from cloud_user.models import UserRegister
from logs import configure_logging
configure_logging(logging.INFO)
log = logging.getLogger(__name__)
log.info("START")
signer = Signer()
def create_signer(user: UserRegister) -> str:
    """
    Читать Readme.COOKIE
    :param user:
    :return:
    """
    hash_bstring = "".encode()
    try:
        
        s = signer.sign(user.email)
        hash_bstring += hashpw_password(s)
    except Exception as e:
        raise ValueError(f"Mistake => {e.__str__()}")
    finally:
        hash_string = hash_bstring.decode("utf-8")
        return hash_string

def hash_check_user_session(pk: int,
                            session_val: str) -> bool:
    """
    
    :param pk: int. Index of single object from db.
    :param session_val: str This is a value from the key of session.
    :return:
    """
    # Get b-code
    status_bool = False
    log.info(f"[{__name__}::hash_check_user_session]: START {pk}: {session_val}")
    try:
        # GET B-CODE
        res = session_val.encode(encoding="utf-8")
        # Get signer
        user_list = UserRegister.objects.filter(id=pk)
        if len(user_list) != 0:
            log.info(f"[{__name__}:{hash_check_user_session.__name__}::hash_check_user_session]: Get  'user_list' > 0")
            s = signer.sign(user_list[0].email)
            # CHECK
            status_bool = bcrypt.checkpw(s.encode("utf-8"), res )
        else:
            log.error(f"[{__name__}::{hash_check_user_session.__name__}]: "
f"Mistake => 'user_list' empty.'pk' invalid." )
            raise ValueError(
                f"[{__name__}::{hash_check_user_session.__name__}]: \
            Mistake => 'user_list' empty. 'pk' invalid."
                )
        log.info(f"[{__name__}::hash_check_user_session]: END")
    except Exception as e:
        log.error(f"[{__name__}::{hash_check_user_session.__name__}]: \
Mistake => {e.__str__()}")
        raise ValueError(f"[{__name__}::{hash_check_user_session.__name__}]: \
Mistake => {e.__str__()}")
    finally:
        return status_bool

def hash_create_user_session(pk: int, session_key: str,
                             live_time: int =86400):
    """
    TODO: Create the hash's value for 'session_key'. Time live is 86400 seconds\
(or 24 hours) This is for the single object from user's db.
    :param pk: int. Index of single object from db.
    :param session_key: str By default is "user_session_{id}". It is the key name/
    :param live_time: int This is a time live for key of session. By the default \
value is the 86400 hours/
    :return: False means what the updates have can not get or Ture,
    """
    log.info(f"[{hash_create_user_session.__name__}]: START {pk}")
    user_list = UserRegister.objects.filter(id=pk)
    if len(user_list) == 0:
        log.error(f"[{__name__}::{hash_create_user_session.__name__}]: \
Mistake => 'user_list' empty. 'pk' invalid.")
        return False
    status_bool = False
    log.info(f"[{__name__}::{hash_create_user_session.__name__}]: \
'user_list' > 0 ")
    try:
        # GREAT SIGNER
        signer = create_signer(user_list[0])
        log.info(f"[{__name__}::hash_create_user_session]: \
Getting signer")
        # SAVE in db the key of session and HASH's value for our key
        session_key = session_key if session_key else f"user_session_{pk}"
        log.info(f"[{__name__}::hash_create_user_session]: \
'session_key': {session_key}")
        cache.set(session_key, signer, live_time)
        log.info(f"[{__name__}::hash_create_user_session]: \
cache.set was successful")
        status_bool = True
    except Exception as e:
        log.error(f"[{__name__}::{hash_create_user_session.__name__}]: \
Mistake => {e.__str__()}")
        raise ValueError(f"[{__name__}::{hash_create_user_session.__name__}]: \
Mistake => {e.__str__()}")
    finally:
        log.info(f"[{__name__}::hash_create_user_session]: END")
        return status_bool
def check(session_key: str, session_val: str, **kwargs) -> False:
    """
    TODO:  Checks the hash from "request.COOKIE.get('user_session_{id}')"  and\
the object single user from db. This the 'single user' take of\
'pk' parameter from the URL.
    :param session_key: 'user_session_{id}'
    :param session_val: str. This the value from "request.COOKIE.get('user_session_{id}')"
    :param kwargs:  We need get the 'pk' parameter from the URL. Index \
of single object from db.)
    :return:
    """
    try:
        log.info(f"[{__name__}::{check.__name__}]: START")
        if not session_val or not session_key:
            log.error(f'[{__name__}::{check.__name__}]: \
not "session_val" or not "session_key"')
            return False
        session_key_value = cache.get(session_key)
        log.info(f"[{__name__}::{check.__name__}]: \
'session_key_value': {session_key_value}")
        # session_key_value_checker = hash_check_user_session(kwargs["pk"], session_key_value)
        session_key_value_checker = hash_check_user_session(kwargs["pk"],
                                                            session_key_value)
        # if not session_key_value or not session_key_value_checker:
        if not session_key_value_checker:
            log.error(f'[{__name__}::{check.__name__}]: \
not session_key_value_checker')
            return False
        # if not session_key_value:
        #     return False
        return True
    except Exception as e:
        raise ValueError(f"[{__name__}::{check.__name__}]: \
Mistake => {e.__str__()}")
    finally:
        log.info(f"[{__name__}::{check.__name__}]: END")
        pass
    
def update(pk: int, session_key: str,
                        live_time: int =86400 ):
    """"
    TODO: Create the new value for 'user_session_{id}'. Time live is 86400 seconds\
(or 24 hours) This is for the single object from user's db.
    :param pk: int. Index of single object from db.
    :param session_key: str. It is the key name
    :param live_time: int This is a time live for session key. By the default \
value is the 86400 hours.
    :return: False means what the updates have can not get or Ture,
    """
    status_bool = False
    log.info(f"[{__name__}::{update.__name__}]: START")
    try:
        status_bool = hash_create_user_session(pk, session_key, live_time)
        log.info(f"[{__name__}::{update.__name__}]: status_bool: {status_bool}")
    except Exception as e:
        log.error(f"[{__name__}::{update.__name__}]: Mistake =>  {e.__str__()}")
        raise ValueError(f'[{__name__}::{update.__name__}]: \
Mistake => {e.__str__()}')
    finally:
        log.info(f"[{__name__}::{update.__name__}]: END")
        return status_bool
