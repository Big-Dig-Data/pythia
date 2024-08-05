import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestBasicInfoAPI:
    def test_system_info_api_view(self, client, settings):
        resp = client.get(reverse('core:system_info_api_view'))
        assert resp.status_code == 200
        data = resp.json()
        assert 'VUFIND_URL' in data
