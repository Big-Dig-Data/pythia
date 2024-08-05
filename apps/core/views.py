from django.conf import settings
from dj_rest_auth.views import PasswordResetConfirmView
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .signals import password_reset_signal


class UserPasswordResetView(PasswordResetConfirmView):
    """
    We have to extend the rest-auth `PasswordResetConfirmView` in order to emit a signal
    on successful reset
    """

    def post(self, request, *args, **kwargs):
        """
        We extend the parent implementation in order to insert a signal. Unfortunately we have
        to duplicate part of the parent code, but it is probably better than replacing it
        completely
        """
        # serialization is done in parent method as well, but we do it once more to get to the
        # user instance which we need for the signal
        # also, we need to do the serialization before we call super().post, because once
        # it is fully processed, the token will no longer be valid and validation will fail
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()  # populates serializer.user
        response = super().post(request, *args, **kwargs)
        password_reset_signal.send(self.__class__, request=request, user=serializer.user)
        return response


class SystemInfoView(GenericAPIView):

    permission_classes = [AllowAny]

    def get(self, request):
        data = {name: getattr(settings, name) for name in settings.EXPORTED_SETTINGS}
        return Response(data)
