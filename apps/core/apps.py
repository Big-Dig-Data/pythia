from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        super().ready()
        # noinspection PyUnresolvedReferences
        from . import signals  # needed to register the signals
