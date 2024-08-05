import factory.fuzzy
import faker

from .. import models

fake = faker.Faker()


class DataSourceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.DataSource
        django_get_or_create = ('slug',)

    slug = factory.Faker('slug')
    data_format = factory.fuzzy.FuzzyChoice([x[0] for x in models.DataSource.FORMAT_CHOICES])
    description = factory.Faker('paragraph')


class DataRecordFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.DataRecord
        django_get_or_create = ('ssid',)

    ssid = factory.Faker('numerify', text='%########')
    isbn13 = factory.Faker('isbn13', separator='')
    source = factory.SubFactory(DataSourceFactory)
    title = factory.Faker('sentence')
