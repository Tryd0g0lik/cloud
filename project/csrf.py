from django.middleware.csrf import CsrfViewMiddleware
from django.core.exceptions import PermissionDenied
from project import use_CSRFToken

class CustomCsrfMiddleware(CsrfViewMiddleware):
    """"
    This is a custom middleware for CSRF token.
     It is for change to the settings.MIDDLEWARE."django.middleware.csrf.CsrfViewMiddleware",
    """
    
    def process_view(self, request, callback, callback_args, callback_kwargs):
        if request.method == 'PATCH' or request.method == 'POST' \
          or request.method == 'PUT' or request.method == 'DELETE':
            csrf_token = request.headers.get('X-CSRFToken')
            if not csrf_token or not use_CSRFToken.state:
                raise PermissionDenied("CSRF token is missing.")
            if csrf_token != use_CSRFToken.state:
                raise PermissionDenied("CSRF token is invalid.")
            return self._accept(request)
        else:
            return super().process_view(
                request, callback, callback_args, callback_kwargs
                )
