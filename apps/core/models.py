from allauth.account.models import EmailAddress, EmailConfirmation
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.functional import cached_property

from .model_mixins import CreatedUpdatedMixin


class User(AbstractUser):

    EMAIL_VERIFICATION_STATUS_UNKNOWN = "unknown"
    EMAIL_VERIFICATION_STATUS_VERIFIED = "verified"
    EMAIL_VERIFICATION_STATUS_PENDING = "pending"
    EMAIL_VERIFICATION_STATUSES = (
        EMAIL_VERIFICATION_STATUS_UNKNOWN,
        EMAIL_VERIFICATION_STATUS_VERIFIED,
        EMAIL_VERIFICATION_STATUS_PENDING,
    )

    def get_usable_name(self):
        if self.first_name or self.last_name:
            return "{0} {1}".format(self.first_name, self.last_name)
        return self.email

    @cached_property
    def email_verification(self) -> dict:
        res = {"status": self.EMAIL_VERIFICATION_STATUS_UNKNOWN, "email_sent": None}
        try:
            # get current email address from allauth
            email_address: EmailAddress = self.emailaddress_set.get(email__iexact=self.email)
            res["status"] = (
                self.EMAIL_VERIFICATION_STATUS_VERIFIED
                if email_address.verified
                else self.EMAIL_VERIFICATION_STATUS_PENDING
            )
            confirmation: EmailConfirmation = email_address.emailconfirmation_set.last()
            if confirmation:
                res["email_sent"] = confirmation.sent

        except (EmailAddress.DoesNotExist, EmailConfirmation.DoesNotExist):
            pass
        return res

    @cached_property
    def email_verified(self):
        return self.EMAIL_VERIFICATION_STATUS_VERIFIED == self.email_verification['status']


class SingletonValue(CreatedUpdatedMixin, models.Model):
    """
    Represents a specific singleton value specified by its key which has to be unique
    """

    key = models.SlugField(unique=True, max_length=50)
    integer = models.IntegerField(null=True)
    float = models.FloatField(null=True)
    date = models.DateTimeField(null=True)
    text = models.TextField(blank=True)

    def __str__(self):
        return self.key
