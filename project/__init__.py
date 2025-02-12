from django.http import JsonResponse


state = ''
class Csrft():
    # pass
    def __init__(self):
        self.state = ''
    def set_state(self, view):
        self.state = view

use_CSRFToken = Csrft()

def decorators_CSRFToken(async_ = False):
    def decorator(func):
        def __wrapper(self, request, *args, **kwargs):
            if request.META.get('HTTP_X_CSRFTOKEN') == use_CSRFToken.state:
                return func(self, request, *args, **kwargs)
            else:
                return JsonResponse({"detail": "CSRF verification failed"}, status=403)
        if async_:
            async def wrapper(self, request, *args, **kwargs):
                return await __wrapper(self, request, *args, **kwargs)
        else:
            def wrapper(self, request, *args, **kwargs):
                return __wrapper(self, request, *args, **kwargs)
        return wrapper
    return decorator
