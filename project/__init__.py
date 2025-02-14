from asgiref.sync import sync_to_async
from django.http import JsonResponse, HttpResponse

state = ''

class Csrft():
    """
    Class Csrft() it is analogous for the 'useState()' from react.
    Here is a task  - create the 'csrftoken' and compare the this 'csrftoken' with \
    'csrftoken' from the request.
    First, we need to get the 'csrftoken' from the cenerator.
    Then we will be compare the 'csrftoken' (backend's version) with \
     the 'csrftoken' (vertion of client) from the request.
    :param state: the state of`'csrftoken'.
    :param set_state: For a set the `'csrftoken' from  csrf-token's generator.
    """
    # pass
    def __init__(self):
        self.state = ''
    def set_state(self, view):
        self.state = view

use_CSRFToken = Csrft()

def decorators_CSRFToken(async_ = False):
    """
    Decorator for methods and for work with the 'csrftoken'.
    :param async_: if True, then the decorator will be async.
    :param func: the function, which will be decorated.
    :return: the function, which will be decorated.
    """
    def decorator(func):
        def __wrapper(self, request, *args, **kwargs):
            if request.META.get('HTTP_X_CSRFTOKEN'):
                if request.META.get('HTTP_X_CSRFTOKEN') == use_CSRFToken.state:
                    return func(self, request, *args, **kwargs)
                else:
                    return JsonResponse({"detail": "CSRF verification failed"}, status=403)
            else:
                return JsonResponse({"detail": "CSRF verification failed"}, status=403)
        if async_:
            async def wrapper(self, request, *args, **kwargs):
                if request.META.get('HTTP_X_CSRFTOKEN'):
                    if request.META.get(
                      'HTTP_X_CSRFTOKEN'
                      ) == use_CSRFToken.state:
                        return await func(self, request, *args, **kwargs)
                    else:
                        return await sync_to_async(JsonResponse)(
                            {"detail": "CSRF verification failed"}, status=403
                            )
                else:
                    return await sync_to_async(JsonResponse)(
                        {"detail": "CSRF verification failed"}, status=403
                        )
        else:
            def wrapper(self, request, *args, **kwargs):
                return __wrapper(self, request, *args, **kwargs)
        return wrapper
    return decorator
