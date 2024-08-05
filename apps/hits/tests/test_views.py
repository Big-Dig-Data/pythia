import pytest
from rest_framework.reverse import reverse


@pytest.mark.django_db
class TestHitStatsViews:
    def test_explicit_topic_stats(self, admin_client, workset):
        url = reverse('hits:explicit-topic-hit-stats', args=[workset.uuid, 'author'])
        response = admin_client.get(url)
        assert response.status_code == 200

    def test_lang_stats(self, admin_client, workset):
        url = reverse("hits:lang-work-stats", args=[workset.uuid])
        response = admin_client.get(url)
        assert response.status_code == 200

    def test_work_category_stats(self, admin_client, workset):
        url = reverse("hits:work-category-work-stats", args=[workset.uuid])
        response = admin_client.get(url)
        assert response.status_code == 200

    def test_owner_institution_stats(self, admin_client, workset):
        url = reverse("hits:owner-institution-work-stats", args=[workset.uuid])
        response = admin_client.get(url)
        assert response.status_code == 200

    def test_explicit_topic_histogram(self, admin_client, workset):
        url = reverse('hits:explicit-topic-hit-histogram', args=[workset.uuid, 'author'])
        response = admin_client.get(url)
        assert response.status_code == 200

    def test_explicit_topic_top_works(self, admin_client, workset):
        url = reverse('hits:explicit-topic-top-works', args=[workset.uuid, 'author'])
        response = admin_client.get(url)
        assert response.status_code == 200


@pytest.mark.django_db
class TestWorkStatsViews:
    def test_workhits_in_time(self, admin_client, work):
        url = reverse('hits:workhits-in-time', args=[work.id])
        response = admin_client.get(url)
        assert response.status_code == 200

    def test_work_hits(self, admin_client, work):
        url = reverse('hits:work-hits', args=[work.id])
        response = admin_client.get(url)
        assert response.status_code == 200
