from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

class CaseInsensitiveEmailBackend(BaseBackend):
    """
    Custom authentication backend that uses email for authentication
    and treats email addresses as case-insensitive.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)

        try:
            # Normalize email to lowercase before authentication
            user = UserModel.objects.get(email__iexact=username)
        except UserModel.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
