import copyreg
from django.apps import AppConfig


class SourceDataConfig(AppConfig):
    name = 'source_data'

    # w/o this django throws an error (Can't pickle memoryview objects)
    # when accessing RawDataRecord.data, more info here
    # https://github.com/noripyt/django-cachalot/issues/125#issuecomment-645926975
    def ready(self):
        # https://docs.python.org/3/library/copyreg.html#copyreg.pickle
        copyreg.pickle(memoryview, lambda val: (memoryview, (bytes(val),)))
