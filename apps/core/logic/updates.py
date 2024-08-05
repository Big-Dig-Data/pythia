from ..models import SingletonValue
from django.utils import timezone


def get_last_date(model_name, logger):
    singleton_name = f'last_update-{model_name}'
    try:
        last_update_singleton = SingletonValue.objects.get(key=singleton_name)
        last_update = last_update_singleton.date
        logger.info('Found last update date: %s', last_update)
    except SingletonValue.DoesNotExist:
        last_update = None
        logger.info('No last update date, processing all works')
    return last_update


def update_last_date(model_name):
    singleton_name = f'last_update-{model_name}'
    SingletonValue.objects.update_or_create(key=singleton_name, defaults={'date': timezone.now()})
