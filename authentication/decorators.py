from django.http import JsonResponse
from functools import wraps


def require_auth(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        auth_user = getattr(request, '_authenticated_user', None)
        if not auth_user:
            return JsonResponse(
                {
                    'error': 'Authentication required',
                    'detail': getattr(request, 'auth_error', 'No valid token provided')
                },
                status=401
            )
        
        if not auth_user.is_active:
            return JsonResponse(
                {'error': 'Account is deactivated'},
                status=401
            )
        
        request.user = auth_user
        return view_func(request, *args, **kwargs)
    
    return wrapper