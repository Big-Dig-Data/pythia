import pytest

from bookrank.models import Publisher, Author, Language
from candidates.logic.sync_candidates_utils import RecordToCandidateDict, NamedModelManager
from candidates.models import Agent
from source_data.models import DataRecord


@pytest.mark.django_db
class TestRecordToCandidateDict:
    def test_map_fields(self, data_records, work_set, isbn):
        record = DataRecord.objects.get(isbn13=isbn)
        agent_map = {(agent.name, agent.email): agent for agent in Agent.objects.all()}
        publisher_manager = NamedModelManager(work_set, Publisher)
        lang_manager = NamedModelManager(work_set, Language)
        author_manager = NamedModelManager(work_set, Author)

        res = RecordToCandidateDict(record, work_set).map_fields(
            agent_map, publisher_manager, lang_manager, author_manager
        )
        assert res == {
            'data': {
                'title': 'Candidates test Title',
                'edition': '1',
                'availability': '20',
                'supplier': 'Candidates Test Supplier',
                'price': '99.95',
                'price_currency': 'EUR',
                'publication_year': '2020',
                'product_format': 'BB',
                'publisher_id': Publisher.objects.get(
                    name='candidates_test_publisher', work_set=work_set
                ).pk,
                'agent': Agent.objects.get(name='Candidates Test Agent'),
                'abstract': 'The book is an in-depth presentation of the European branch'
                ' of semiotic theory, originating in the work of Ferdinand de Saussure.',
                'extra_data': {
                    'RecordReference': '56653307',
                    'ProductIdentifier': {'ProductIDType': '15', 'IDValue': '9783110616231'},
                    'Subject': {
                        'SubjectSchemeIdentifier': '24',
                        'SubjectSchemeName': 'JL1',
                        'SubjectHeadingText': 'Humanities',
                    },
                    'MediaFile': {
                        'MediaFileTypeCode': '04',
                        'MediaFileLinkTypeCode': '01',
                        'MediaFileLink': 'https://www.degruyter.com/cover/covers/9783110616231.jpg',
                    },
                },
            },
            'publishers_created': True,
            'agents_created': True,
            'authors': {
                'entries': [Author.objects.get(name='Candidates, Test Author').pk],
                'num_created': 1,
            },
            'languages': {
                'entries': [Language.objects.get(name='candidates_test_lang').pk],
                'num_created': 1,
            },
        }
        assert len(lang_manager.name_to_obj) == 1
