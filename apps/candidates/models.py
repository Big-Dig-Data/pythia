from decimal import Decimal

from django.db import models
from django.db.models import JSONField
from django.contrib.auth import get_user_model

from bookrank.models import Work
from core.model_mixins import CreatedUpdatedMixin
from .managers import CandidateManager


class Agent(CreatedUpdatedMixin, models.Model):
    '''
    stores MarketAgent (source) info
    '''

    name = models.CharField(max_length=200)
    email = models.EmailField()

    def __str__(self) -> str:
        return self.name


class AuthorCandidate(models.Model):
    topic = models.ForeignKey('bookrank.Author', on_delete=models.CASCADE)
    candidate = models.ForeignKey('Candidate', on_delete=models.CASCADE)


class LanguageCandidate(models.Model):
    topic = models.ForeignKey('bookrank.Language', on_delete=models.CASCADE)
    candidate = models.ForeignKey('Candidate', on_delete=models.CASCADE)


class SubjectCategoryCandidate(models.Model):
    topic = models.ForeignKey('bookrank.SubjectCategory', on_delete=models.CASCADE)
    candidate = models.ForeignKey('Candidate', on_delete=models.CASCADE)


class UserBookmarkedCandidate(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    candidate = models.ForeignKey('Candidate', on_delete=models.CASCADE)


class UserBlacklistedCandidate(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    candidate = models.ForeignKey('Candidate', on_delete=models.CASCADE)


class Candidate(CreatedUpdatedMixin, models.Model):
    isbn = models.CharField(max_length=20, db_index=True)
    title = models.CharField(max_length=500)
    authors = models.ManyToManyField(
        'bookrank.Author', related_name='candidates', through=AuthorCandidate, blank=True
    )
    languages = models.ManyToManyField(
        'bookrank.Language', related_name='candidates', through=LanguageCandidate, blank=True
    )
    abstract = models.TextField(blank=True)
    edition = models.IntegerField(blank=True, null=True)

    publisher = models.ForeignKey(
        'bookrank.Publisher',
        on_delete=models.CASCADE,
        related_name='candidates',
        blank=True,
        null=True,
    )
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, blank=True, null=True)
    supplier = models.CharField(max_length=200, blank=True)
    subjects = models.ManyToManyField(
        'bookrank.SubjectCategory',
        related_name='candidates',
        through=SubjectCategoryCandidate,
        blank=True,
    )

    availability = models.IntegerField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal(0))
    price_currency = models.CharField(max_length=10, blank=True)
    publication_year = models.IntegerField(blank=True, null=True)
    product_format = models.CharField(max_length=8, blank=True)

    bookmarked_by = models.ManyToManyField(
        get_user_model(),
        related_name='bookmarked_candidates',
        through=UserBookmarkedCandidate,
        blank=True,
    )
    blacklisted_by = models.ManyToManyField(
        get_user_model(),
        related_name='blacklisted_candidates',
        through=UserBlacklistedCandidate,
        blank=True,
    )

    extra_data = JSONField(default=dict)
    static_scores = JSONField(
        default=dict,
        help_text='stores scores accumulated from static scores of related languages, publishers,'
        ' etc.',
    )
    normalized_scores = JSONField(
        default=dict,
        help_text='stores scores accumulated from normalized scores of related languages, publishers,'
        ' etc.',
    )
    data_record = models.OneToOneField('source_data.DataRecord', on_delete=models.CASCADE)
    matched_works = models.ManyToManyField(
        Work, through='CandidateWorkLink', related_name='matched_candidates'
    )

    objects = CandidateManager()


class CandidateWorkLink(models.Model):

    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    work = models.ForeignKey(Work, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('candidate', 'work'),)

    @classmethod
    def create_missing_links(cls) -> int:
        """
        Creates links between works and candidates if the are not already present
        :return:
        """
        isbn_to_cand = {
            c['isbn']: c['id'] for c in Candidate.objects.exclude(isbn='').values('id', 'isbn')
        }
        existing_links = {
            (rec['work_id'], rec['candidate_id'])
            for rec in CandidateWorkLink.objects.values('candidate_id', 'work_id')
        }
        to_create = set()
        for work in Work.objects.filter(isbn__len__gte=1).iterator():
            for isbn in work.isbn:
                if isbn in isbn_to_cand:
                    link_ids = (work.pk, isbn_to_cand[isbn])
                    if link_ids not in existing_links:
                        to_create.add(link_ids)
        CandidateWorkLink.objects.bulk_create(
            CandidateWorkLink(candidate_id=cid, work_id=wid) for wid, cid in to_create
        )
        return len(to_create)


class CandidatesSettings(models.Model):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="candidates_settings"
    )
    name = models.CharField(max_length=100)
    internal = models.BooleanField(default=False)
    settings_obj = JSONField(null=True)
