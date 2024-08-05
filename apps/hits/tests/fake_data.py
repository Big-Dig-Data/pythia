import factory.fuzzy
import faker
from django.utils.text import slugify

from bookrank.tests.fake_data import WorkFactory
from .. import models

fake = faker.Faker()

hit_types = ['absence loans', 'presence loans']


class HitTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.HitType
        django_get_or_create = ("slug",)

    name = factory.fuzzy.FuzzyChoice(hit_types)
    slug = factory.LazyAttribute(lambda o: slugify(o.name))


class WorkHitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.WorkHit
        django_get_or_create = ("work", "typ", "date")

    work = factory.SubFactory(WorkFactory)
    typ = factory.SubFactory(HitTypeFactory)
    date = factory.Faker('date_this_decade')
    value = factory.Faker('random_int', min=1, max=100)
