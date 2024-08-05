import factory
import faker

from bookrank.tests.fake_data import AuthorFactory, PublisherFactory
from source_data.tests.fake_data import DataRecordFactory
from .. import models

fake = faker.Faker()


class CandidateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Candidate
        django_get_or_create = ('isbn',)

    isbn = factory.Faker('isbn13', separator='')
    title = factory.Faker('sentence')
    abstract = factory.Faker('paragraph')
    supplier = factory.Faker('company')
    price = factory.Faker('random_int', min=1, max=1000)
    price_currency = factory.Faker('currency_code')
    publication_year = factory.Faker('random_int', min=1950, max=2022)
    availability = 20
    data_record = factory.SubFactory(DataRecordFactory)
    publisher = factory.SubFactory(PublisherFactory)

    @factory.post_generation
    def authors(obj, create, extracted, **kwargs):
        if extracted:
            obj.authors.set(extracted)
        elif obj.pk:
            AuthorCandidateFactory.create_batch(fake.random_int(min=0, max=6), candidate=obj)

    @factory.post_generation
    def subjects(obj, create, extracted, **kwargs):
        # we only assign what has been explicitly set, otherwise nothing
        if extracted:
            obj.subjects.set(extracted)


class AuthorCandidateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.AuthorCandidate
        django_get_or_create = ('topic', 'candidate')

    topic = factory.SubFactory(AuthorFactory)
    candidate = factory.SubFactory(CandidateFactory)
