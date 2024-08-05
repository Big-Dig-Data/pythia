from uuid import uuid4

from django.conf import settings
from django.db.models import JSONField
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from core.model_mixins import CreatedUpdatedMixin
from .managers import SubjectCategoryManager, ETManager, WorkManager

TYP_AUTHOR = 1
TYP_KEYWORD = 2
TYP_LANG = 3
TYP_PUBLISHER = 4
TYP_CATEGORY = 100
TYP_GENERATED = 255


class WorkSet(CreatedUpdatedMixin, models.Model):

    uuid = models.UUIDField(default=uuid4, unique=True)
    name = models.TextField(blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        return self.name or str(self.uuid)


class ExplicitTopic(CreatedUpdatedMixin, models.Model):

    IS_CONTROLLED_DICTIONARY = False  # True if there is some external controlled source of data

    name = models.CharField(max_length=250)
    work_set = models.ForeignKey(WorkSet, on_delete=models.CASCADE)
    # used for calculating candidate score
    static_score = JSONField(default=dict, blank=True)
    normalized_score = JSONField(default=dict)
    # static growth fields
    score_past_yr = models.IntegerField(blank=True, null=True)
    score_yr_b4 = models.IntegerField(blank=True, null=True)
    absolute_growth = models.IntegerField(blank=True, null=True)
    relative_growth = models.FloatField(blank=True, null=True)

    objects = ETManager()

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Publisher(ExplicitTopic):

    pass


class Author(ExplicitTopic):

    pass


class Language(ExplicitTopic):

    pass


class WorkCategory(ExplicitTopic):
    class Meta:
        verbose_name_plural = "Work categories"


class OwnerInstitution(ExplicitTopic):

    pass


class SubjectCategory(ExplicitTopic, MPTTModel):
    """
    This explicit topic is used for PSH and other subject category hierarchies.
    Each subtree represents one type of topic hierarchy
    """

    IS_CONTROLLED_DICTIONARY = True

    uid = models.CharField(max_length=32, unique=True)
    is_controlled_dictionary = models.BooleanField(
        default=True,
        help_text='When true, the subtree is fixed and should not be extended during export - '
        'used for top-level nodes only',
    )
    parent = TreeForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='children'
    )

    objects = SubjectCategoryManager()


class PublisherWork(models.Model):

    topic = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    work = models.ForeignKey('Work', on_delete=models.CASCADE)


class AuthorWork(models.Model):

    topic = models.ForeignKey(Author, on_delete=models.CASCADE)
    work = models.ForeignKey('Work', on_delete=models.CASCADE)


class SubjectCategoryWork(models.Model):

    topic = models.ForeignKey(SubjectCategory, on_delete=models.CASCADE)
    work = models.ForeignKey('Work', on_delete=models.CASCADE)


class Work(CreatedUpdatedMixin, models.Model):

    uid = models.CharField(max_length=64)
    name = models.TextField(blank=True)
    isbn = ArrayField(models.CharField(max_length=15), default=list)
    work_set = models.ForeignKey(WorkSet, on_delete=models.CASCADE, related_name='works')
    abstract = models.TextField(blank=True)
    extra_data = JSONField(default=dict, blank=True)
    # explicit topics
    category = models.ForeignKey(
        WorkCategory, null=True, on_delete=models.SET_NULL, related_name='works'
    )
    lang = models.ForeignKey(Language, null=True, on_delete=models.SET_NULL, related_name='works')
    owner_institution = models.ForeignKey(
        OwnerInstitution,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='works',
        help_text='Owner library identification',
    )
    publishers = models.ManyToManyField(Publisher, related_name='works', through=PublisherWork)
    authors = models.ManyToManyField(Author, related_name='works', through=AuthorWork)
    subject_categories = models.ManyToManyField(
        SubjectCategory, related_name='works', through=SubjectCategoryWork
    )
    # non-foreign key "topics"
    catalog_date = models.DateField(
        null=True, help_text='Date on which this work was added into the catalogue'
    )
    start_yop = models.PositiveSmallIntegerField(
        null=True, blank=True, help_text='Start year of publication'
    )
    end_yop = models.PositiveSmallIntegerField(
        null=True, blank=True, help_text='End year of publication'
    )
    acquisition_date = models.DateField(blank=True, null=True)
    # static field for sum of the loans that happened 1 year after acquisition_date
    acquisition_score = models.IntegerField(default=0)
    # static growth fields
    score_past_yr = models.IntegerField(default=0, help_text='Sum of hits for one year from now')
    score_yr_b4 = models.IntegerField(
        default=0, help_text='Sum of hits between two years and one year from now'
    )
    absolute_growth = models.IntegerField(
        default=0, help_text='Difference between `score_past_yr` and `score_yr_b4`'
    )
    relative_growth = models.FloatField(
        blank=True, null=True, help_text='`absolute_growth` divided by `score_yr_b4`'
    )

    objects = WorkManager()

    class Meta:
        unique_together = ('uid', 'work_set')

    def __str__(self):
        if self.name:
            return "{}: {}".format(self.uid, self.name)
        else:
            return self.uid

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.topics_ = []

    @property
    def cover_image_url(self):
        if settings.COVER_IMAGE_TEMPLATE:
            return settings.COVER_IMAGE_TEMPLATE.format(self)
        return None


class WorkCopy(CreatedUpdatedMixin, models.Model):
    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name="copies")
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    currency = models.CharField(max_length=10, null=True)
    acquisition_date = models.DateField(null=True)
