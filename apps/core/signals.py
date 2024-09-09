from allauth.account.models import EmailAddress
from allauth.account.signals import user_signed_up
from django.core.mail import mail_admins
from django.dispatch import receiver, Signal


password_reset_signal = Signal()


@receiver(user_signed_up)
def mail_about_user_signing_up(request, user, **kwargs):
    mail_admins(
        "New account created",
        "New user account was created.\n\nUsername: {0.username}\nEmail: {0.email}".format(user),
    )


@receiver(password_reset_signal)
def verify_user_email(request, user, **kwargs):
    """
    After successful password reset, we take the users default email as verified.
    Also, if the appropriate `EmailAddress` instance does not exist, we create it.
    """
    if user.email and not user.email_verified:
        email_obj, created = EmailAddress.objects.get_or_create(
            user=user, email=user.email, defaults={'verified': True}
        )
        if not created:
            email_obj.verified = True
            email_obj.save()
