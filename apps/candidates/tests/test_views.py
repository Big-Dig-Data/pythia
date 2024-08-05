import json

import pytest
from django.core.management import call_command
from django.urls import reverse

from bookrank.models import Author, Work
from candidates.models import Candidate, CandidatesSettings
from candidates.tests.fake_data import CandidateFactory

WORK_ISBNS = [['9780934951326', '9789811219610'], ['9789811223327'], ['9781782628330']]


@pytest.fixture()
def works(work_set):
    return [
        Work.objects.create(isbn=isbn, work_set=work_set, uid='-'.join(isbn)) for isbn in WORK_ISBNS
    ]


@pytest.mark.django_db()
class TestCandidateViewSet:
    def helper(self, client, q=None):
        url = reverse('candidates:candidates-list')
        resp = client.get(url, q)
        assert resp.status_code == 200
        return resp.data['results']

    def test_list(self, admin_client, candidates):
        results = self.helper(admin_client)
        assert len(results) == candidates.count()

    def test_list_search(self, admin_client, candidates, isbn):
        results = self.helper(admin_client, q={'search': 'candidates test'})
        assert len(results) == 1
        assert results[0]['isbn'] == isbn

    def test_list_order(self, admin_client, candidates):
        results = self.helper(admin_client, q={'order_by': '-isbn'})
        resp_isbns = [obj['isbn'] for obj in results]
        assert resp_isbns == list(candidates.order_by('-isbn').values_list('isbn', flat=True))
        assert len(results) == candidates.count()

    def test_list_filters(self, admin_client, candidates, isbn):
        author = Author.objects.get(name='Candidates, Test Author')
        q = {'filters': json.dumps({"author": [author.pk]})}
        results = self.helper(admin_client, q=q)
        assert len(results) == 1
        assert results[0]['isbn'] == isbn

    def test_list_work_filter(self, admin_client, candidates, works, isbn):
        call_command('create_missing_candidate_work_links')
        results = self.helper(admin_client, q={'works_filter': '1'})
        assert len(results) == 1
        assert results[0]['isbn'] == isbn


@pytest.mark.django_db()
class TestCandidateFactory:
    def test_factory(self):
        candidates = CandidateFactory.create_batch(5)
        # due to get_or_create less than 5 unique objects might be created
        assert Candidate.objects.count() == len({c.pk for c in candidates})


@pytest.mark.django_db()
class TestCandidateSettings:
    @pytest.mark.parametrize(['default_exists'], [(True,), (False,)])
    def test_list_creates_default_if_missing(self, admin_client, admin_user, default_exists):
        assert CandidatesSettings.objects.count() == 0
        if default_exists:
            CandidatesSettings.objects.create(
                user=admin_user, internal=True, name='default', settings_obj={}
            )
        resp = admin_client.get(reverse('candidates:candidates_settings-list'))
        assert resp.status_code == 200
        assert CandidatesSettings.objects.count() == 1, 'one profile must exists by now'
        assert len(resp.json()) == 1
        assert (
            CandidatesSettings.objects.filter(
                internal=True, name='default', user=admin_user
            ).exists(),
            (
                'default profile is the one existing'
                if default_exists
                else 'default profile was created for the user at hand'
            ),
        )

    @pytest.mark.parametrize(['default_exists'], [(True,), (False,)])
    def test_default_profile(self, admin_client, admin_user, default_exists):
        assert CandidatesSettings.objects.count() == 0
        if default_exists:
            CandidatesSettings.objects.create(
                user=admin_user, internal=True, name='default', settings_obj={}
            )
        resp = admin_client.get(reverse('candidates:candidates_settings-default-profile'))
        assert resp.status_code == 200
        assert CandidatesSettings.objects.count() == 1, 'one profile must exists by now'
        assert (
            resp.json()['pk']
            == CandidatesSettings.objects.get(internal=True, name='default', user=admin_user).pk
        )
