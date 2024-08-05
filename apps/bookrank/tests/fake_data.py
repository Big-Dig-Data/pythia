from typing import Optional

import factory.fuzzy
import faker

from .. import models


fake = faker.Faker()


def random_isbns(length: Optional[int] = None):
    """
    `length` is number of None for random number
    """
    if length is None:
        length = fake.random_int(min=0, max=5)
    return [fake.isbn13(separator='') for _ in range(length)]


class WorkSetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.WorkSet
        django_get_or_create = ('name',)

    name = 'Aleph'


class AuthorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Author
        django_get_or_create = ('name',)

    name = factory.Faker('name')
    work_set = factory.SubFactory(WorkSetFactory)


class PublisherFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Publisher
        django_get_or_create = ('name',)

    name = factory.Faker('company')
    work_set = factory.SubFactory(WorkSetFactory)


class LanguageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Language
        django_get_or_create = ('name',)

    name = factory.Faker('language_code')
    work_set = factory.SubFactory(WorkSetFactory)


class WorkFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Work
        django_get_or_create = ("uid",)

    uid = factory.Faker('numerify', text='%########')
    name = factory.Faker('sentence')
    isbn = factory.LazyFunction(random_isbns)
    lang = factory.SubFactory(LanguageFactory)
    work_set = factory.SubFactory(WorkSetFactory)

    @factory.post_generation
    def authors(obj, create, extracted, **kwargs):
        if extracted is not None:
            obj.authors.set(extracted)
        elif obj.pk:
            AuthorWorkFactory.create_batch(
                fake.random_int(min=0, max=6), work=obj, topic__work_set=obj.work_set
            )

    @factory.post_generation
    def publishers(obj, create, extracted, **kwargs):
        if extracted is not None:
            obj.publishers.set(extracted)
        elif obj.pk:
            PublisherWorkFactory.create_batch(
                fake.random_int(min=1, max=3), work=obj, topic__work_set=obj.work_set
            )

    @factory.post_generation
    def subject_categories(obj, create, extracted, **kwargs):
        # we only assign what has been explicitly set, otherwise nothing
        if extracted:
            obj.subject_categories.set(extracted)


class TopicWorkLinkFactory(factory.django.DjangoModelFactory):
    class Meta:
        django_get_or_create = ('topic', 'work')

    work = factory.SubFactory(WorkFactory)


class AuthorWorkFactory(TopicWorkLinkFactory):
    class Meta:
        model = models.AuthorWork

    topic = factory.SubFactory(AuthorFactory)


class PublisherWorkFactory(TopicWorkLinkFactory):
    class Meta:
        model = models.PublisherWork

    topic = factory.SubFactory(PublisherFactory)


class WorkCopyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.WorkCopy

    work = factory.SubFactory(WorkFactory)
    price = factory.Faker('random_int', min=10, max=500)
    currency = factory.Faker('currency_code')
    acquisition_date = factory.Faker('date_this_century')
