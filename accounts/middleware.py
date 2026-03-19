from accounts.models import ActivityLog
from django.contrib.auth.models import AnonymousUser


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class ActivityLoggingMiddleware:
    """Middleware to log user activities and login/logout events"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if user is being authenticated (login)
        if request.path == '/accounts/login/' and request.method == 'POST':
            username = request.POST.get('username')
            if username:
                # Log after successful login will be handled in the view
                pass

        response = self.get_response(request)

        # Log logout
        if request.path == '/accounts/logout/' and hasattr(request, 'user') and request.user.is_authenticated:
            ip_address = get_client_ip(request)
            ActivityLog.objects.create(
                user=request.user,
                action='logout',
                description=f"User {request.user.username} logged out from {ip_address}",
                affected_entity=f"User: {request.user.username}",
                ip_address=ip_address,
                status='success'
            )

        return response


class ExceptionLoggingMiddleware:
    """Middleware to log permission denied and exception events"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Log permission denied (403 Forbidden)
        if response.status_code == 403 and hasattr(request, 'user') and request.user.is_authenticated:
            ip_address = get_client_ip(request)
            ActivityLog.objects.create(
                user=request.user,
                action='permission_denied',
                description=f"User {request.user.username} attempted to access {request.path} without permission",
                affected_entity=request.path,
                ip_address=ip_address,
                status='warning'
            )

        return response
