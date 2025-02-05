
def get_data_authenticate(request) -> object:
    """
    TODO: function gets the user data from user request. They, after can use to \
the authenticate of user.
    :param request: From the `request.COOKIES` we receiving data.
    :return: object of '{ \
    user_id: id, \
    user_session: <user_session_<id>'s value>, \
    is_superuser: <is_superuser_<id>'s value>\
        }' if everything went well or \
    returns the empty object if everything went not well.
    """
    class CookieData:
        pass
    instance = CookieData()
    
    try:
        # key_list = request.COOKIES.keys()
        # if len(list(key_list)) == 0:
        #     raise ValueError(
        #         f"[{__name__}::{get_data_authenticate.__name__}]: \
        #     Mistake => 'request.COOKIE' is invalid."
        #         )
        # user_session_key_list = \
        #     [key for key in list(key_list) if r"user_session_" in key]
        # if len(user_session_key_list) != 0:
        #     numb = user_session_key_list[0].split("_")[-1]
        
        index = request.COOKIES.get("index")
        
        # import re
        # match = re.search(r"[^v1]\d{1,}", request.path)
        # if not index and match:
        #     index = request.path[match.start() + 1: match.end()]
        if ( not index):
            return {}
        setattr(instance, "id", index)
        setattr(instance,  "user_session", \
                request.COOKIES.get(f"user_session"))
        #request.COOKIES.get(f"user_session_{index}"))
        setattr(instance, "is_superuser", \
                request.COOKIES.get(f"is_superuser"))
        # request.COOKIES.get(f"is_superuser_{index}"))
    except Exception as e:
        
        raise ValueError(f"[{__name__}::{get_data_authenticate.__name__}]: \
Mistake => {e.__str__()}")
    finally:
        return instance