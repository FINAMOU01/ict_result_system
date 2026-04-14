from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


class EmailAuthenticationBackend(ModelBackend):
    """
    Custom authentication backend that allows users to authenticate with email and password
    instead of username and password.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate using email instead of username.
        The 'username' parameter is actually the email in this backend.
        """
        try:
            # Treat the 'username' parameter as email
            user = CustomUser.objects.get(email=username)
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except CustomUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        """
        Get user by ID (standard method required by authentication backend)
        """
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None
