def get_data_authenticate(request) -> object:
    """
    TODO: function gets the user data from user request. They, after can use to \
the authenticate of user.
    :param request: From the `request.COOKIES` we receiving data.
    :return: object of '{ \
    user_id: id, \
    user_session: <user_session_<id>'s value>, \
    is_staff: <is_staff_<id>'s value>\
        }' if everything went well or \
    returns the empty object if everything went not well.
    """

    class CookieData:
        pass

    instance = CookieData()

    try:
        index = request.COOKIES.get("index")

        if not index:
            return instance
        setattr(instance, "id", index)
        setattr(instance, "user_session", request.COOKIES.get(f"user_session"))

        # setattr(instance, "user_superuser", \
        #         request.COOKIES.get(f"is_staff"))

    except Exception as e:

        raise ValueError(
            f"[{__name__}::{get_data_authenticate.__name__}]: \
Mistake => {e.__str__()}"
        )
    finally:
        return instance


def decrypt_data(encrypted_data: str, secret_key: str) -> str:
    """
    Encryption
    https://pycryptodome.readthedocs.io/en/latest/src/cipher/classic.html
    Decodes an encrypted string
    :param encrypted_data:
    :param secret_key:
    :return:
    """
    import logging
    from array import array
    from base64 import b64decode

    from Crypto.Cipher import AES

    from logs import configure_logging

    configure_logging(logging.INFO)
    log = logging.getLogger(__name__)

    status_data = ""
    __text = f"{__name__}{decrypt_data.__name__}"
    log.info(f"[{__text}] START")
    try:
        secret_key_int_array = array("B", secret_key.encode())
        # print()
        numb_str = "".join(map(str, list(secret_key_int_array)))
        key = numb_str[:32].encode()  # 32
        iv = numb_str[:16].encode()  # 16
        cipher = AES.new(key, AES.MODE_CBC, iv)
        # (unpad(cipher.decrypt(decrypted_data), AES.block_size)).decode()
        ct = b64decode(encrypted_data)
        pt = cipher.decrypt(ct)
        # encrypted_data_bytes = base64.b64decode(ct)
        status_data += pt.decode().strip("").strip("\\x01").strip("")
    except Exception as e:
        log.error(f"[{__text}] ERROR: {str(e)}")
        raise ValueError(f"[{__text}] Mistake => to the decrypt: {str(e)}")
    finally:
        log.info(f"[{__name__}{decrypt_data.__name__}] END")
    return status_data
