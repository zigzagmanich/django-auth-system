from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from authentication.models import User, Session
from django.utils import timezone


class CustomAuthMiddleware(MiddlewareMixin):

    def process_request(self, request):
        
        public_paths = [
            '/api/auth/register/',
            '/api/auth/login/',
            '/admin/',
        ]

        if any(request.path.startswith(path) for path in public_paths):
            request._authenticated_user = None
            return None

        token = self._extract_token(request)

        if not token:
            print("No token")
            request._authenticated_user = None
            request.auth_error = None
            return None

        user = self._authenticate_token(token)
        
        if user:
            request._authenticated_user = user
            request.auth_error = None
        else:
            request._authenticated_user = None
            request.auth_error = "Invalid or expired token"
        return None

    def _extract_token(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            return auth_header[7:]
        return None

    def _authenticate_token(self, token):
        try:
            session = Session.objects.select_related('user', 'user__role').filter(
                session_token=token
            ).first()

            if not session:
                return None

            if not session.is_valid():
                session.delete()
                return None

            return session.user
        except Exception:
            return None