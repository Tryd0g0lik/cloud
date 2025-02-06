
def  get_data_authenticate(request) -> object:
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
        index = request.COOKIES.get("index")
        
        if ( not index):
            return {}
        setattr(instance, "id", index)
        setattr(instance,  "user_session", \
                request.COOKIES.get(f"user_session"))
        
        setattr(instance, "is_superuser", \
                request.COOKIES.get(f"is_superuser"))
        
    except Exception as e:
        
        raise ValueError(f"[{__name__}::{get_data_authenticate.__name__}]: \
Mistake => {e.__str__()}")
    finally:
        return instance