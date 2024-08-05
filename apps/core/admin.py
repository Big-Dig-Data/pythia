from allauth.account.adapter import get_adapter
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin

from .models import User, SingletonValue


@admin.register(User)
class UserAdmin(UserAdmin):

    actions = ['send_invitation_emails']

    def send_invitation_emails(self, request, queryset):
        adapter = get_adapter()
        sent_messages = 0
        for user in queryset.all():
            adapter.send_invitation_email(request, user)
            sent_messages += 1
        messages.add_message(request, messages.SUCCESS, f'Sent {sent_messages} invitation(s)')

    send_invitation_emails.allowed_permissions = ('change',)


@admin.register(SingletonValue)
class SingletonValueAdmin(admin.ModelAdmin):

    list_display = ['key', 'integer', 'float', 'date', 'text', 'last_updated']
