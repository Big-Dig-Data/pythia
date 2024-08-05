from django.conf import settings
from rest_auth.serializers import PasswordResetSerializer


class PythiaPasswordResetSerializer(PasswordResetSerializer):
    def get_email_options(self):
        out = super().get_email_options()
        return out
