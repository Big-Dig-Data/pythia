import pytest
from django.core.management import call_command

from aleph.models import AlephEntry


@pytest.mark.django_db
class TestAlephSync:
    def test_simple_sync(self):
        assert AlephEntry.objects.count() == 0
        call_command('import_aleph_marc_xml', '--disable-transactions', 'apps/aleph/tests/data')
        assert AlephEntry.objects.count() == 2
        assert set(AlephEntry.objects.all().values_list('uid', flat=True)) == {
            '000000002',
            '000010000',
        }

    @pytest.mark.parametrize(['extra_fields', 'has_extra_key'], [('', False), ('914', True)])
    def test_custom_fields(self, settings, extra_fields, has_extra_key):
        settings.EXTRA_ALEPH_FIELDS = extra_fields
        call_command('import_aleph_marc_xml', '--disable-transactions', 'apps/aleph/tests/data')
        assert AlephEntry.objects.count() == 2
        entry = AlephEntry.objects.get(uid='000000002')
        if has_extra_key:
            assert '_extra' in entry.raw_data
            fields = extra_fields.split(',')
            for field in fields:
                assert field.strip() in entry.raw_data['_extra']
        else:
            assert '_extra' not in entry.raw_data
