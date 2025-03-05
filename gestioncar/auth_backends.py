# gestioncar/auth_backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmailAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        try:
            user = User.objects.get(email=username)  # Busca por email
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
        return None