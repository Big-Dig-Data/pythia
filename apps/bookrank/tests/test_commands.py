from collections import Counter
from datetime import date, timedelta

import pytest
from django.core.management import call_command
from django.utils.timezone import now

from aleph.models import AlephEntry
from bookrank.logic.cleanup import remove_unpaired_quotes, normalize_name
from bookrank.logic.static_score import YEARS, update_static_scores
from bookrank.models import Author, Publisher, SubjectCategory, Work, WorkSet
from bookrank.tests.fake_data import WorkFactory
from candidates.models import Candidate
from hits.models import WorkHit
from hits.tests.fake_data import WorkHitFactory

THEMA_CREATE_FILE = 'apps/bookrank/tests/data/thema_cats.json'
THEMA_UPDATE_FILE = 'apps/bookrank/tests/data/thema_cats_update.json'
THEMA_UIDS = [['J'], ['JM'], ['JMA']]
AUTHOR_NAMES = ['Doe, John ', ' Doe, John,', 'Doe, John!']
PUBLISHER_NAMES = ['John Doe&sons ', 'John Doe & sons', 'John  Doe  & sons']
CANDIDATES_DATA = [
    {'isbn': '111', 'title': 'Candidate 1'},
    {'isbn': '222', 'title': 'Candidate 2'},
    {'isbn': '333', 'title': 'Candidate 3'},
]
QUOTES_STRS = [
    ('Verlag "Die Braunkohle"', 'Verlag "Die Braunkohle"'),
    ('"Ver"lag "Die Braunkohle" "w"', 'Verlag "Die Braunkohle" "w"'),
    ('"Foo"', '"Foo"'),
    ('Foo"', 'Foo'),
    ('The "Foo"', 'The "Foo"'),
    ('The "Foo""', 'The "Foo"'),
    ('The ""Foo"', 'The "Foo"'),
]
NORMALIZATION_STRS = [
    ('Landolt, /Hans/', 'Landolt, Hans'),
    ('-ab/gk-', '-ab/gk-'),
    ('ab / gk-', 'ab gk'),
    ('March, Francis Andrew, |d 1825-1911', 'March, Francis Andrew'),
    ('Lassar=Cohn', 'Lassar-Cohn'),
    (
        'Ministe;rstvo les. a vod. hospodářství ČSR ; Hydroprojekt;',
        'Ministerstvo les. a vod. hospodářství ČSR ; Hydroprojekt',
    ),
    ('Nakladat:elství techn. lit. : Alfa:', 'Nakladatelství techn. lit. : Alfa'),
    ('Architects, Lake|Flato', 'Architects, Lake|Flato'),
    ('Architects, Lake|', 'Architects, Lake'),
    # | followed by a single letter or number after a space means throw the rest away
    ('Monfred, J. B. |4 aut', 'Monfred, J. B.'),
    ('Kirk, Raymond E. |q (Raymond Eller), |d 1890-1957', 'Kirk, Raymond E.'),
    # we do not throw the rest after | away here - it is part of string
    ('Aero-klub Praha, 5. Z|O Svazarmu', 'Aero-klub Praha, 5. Z|O Svazarmu'),
]


@pytest.mark.django_db
class TestMakeThemaTree:
    def test_create(self, work_set):
        call_command('make_thema_tree', work_set, THEMA_CREATE_FILE)
        subjects = SubjectCategory.objects.all()
        assert subjects.count() == 4
        for cat in subjects:
            if cat.uid == 'THEMA-ROOT':
                assert cat.parent is None
                assert cat.is_controlled_dictionary
            elif len(cat.uid) == 1:
                assert cat.parent == subjects.get(uid='THEMA-ROOT')
                assert not cat.is_controlled_dictionary
            else:
                assert cat.parent.uid == cat.uid[:-1]
                assert not cat.is_controlled_dictionary

    def test_update(self, work_set):
        call_command('make_thema_tree', work_set, THEMA_CREATE_FILE)
        call_command('make_thema_tree', work_set, THEMA_UPDATE_FILE)
        subjects = SubjectCategory.objects.all()
        assert subjects.count() == 4
        subjects = subjects.exclude(uid='THEMA-ROOT')
        assert all(cat.name.endswith(' update') for cat in subjects)


@pytest.mark.django_db
class TestCategorizeWorksByThema:
    def test_command(self, work_set, works):
        call_command('make_thema_tree', work_set, THEMA_CREATE_FILE)
        call_command('categorize_works_by_thema', work_set)
        thema_tree_id = SubjectCategory.objects.get(uid='THEMA-ROOT').tree_id
        for i, work in enumerate(works):
            assert (
                list(
                    work.subject_categories.filter(tree_id=thema_tree_id).values_list(
                        'uid', flat=True
                    )
                )
                == THEMA_UIDS[i]
            )


@pytest.mark.django_db
class TestNormalizeAuthorsAndPublishers:
    def test_command(self, work_set, works, data_records):
        authors = Author.objects.bulk_create(
            [Author(name=name, work_set=work_set) for name in AUTHOR_NAMES]
        )
        publishers = Publisher.objects.bulk_create(
            [Publisher(name=name, work_set=work_set) for name in PUBLISHER_NAMES]
        )
        candidates = Candidate.objects.bulk_create(
            [
                Candidate(**data, data_record=data_records[i])
                for i, data in enumerate(CANDIDATES_DATA)
            ]
        )
        for author, pub, work, candidate in zip(authors, publishers, works, candidates):
            work.authors.add(author)
            work.publishers.add(pub)
            candidate.authors.add(author)
            candidate.publisher = pub
            candidate.save()
        call_command('normalize_authors_and_publishers', work_set.name)
        authors = Author.objects.all()
        assert authors.count() == 1
        assert authors.first().name == 'Doe, John'
        publishers = Publisher.objects.all()
        assert publishers.count() == 2
        assert publishers.last().name == 'John Doe & sons'
        assert (
            list(works[0].authors.values_list('pk', flat=True))
            == list(works[1].authors.values_list('pk', flat=True))
            == list(works[2].authors.values_list('pk', flat=True))
            == [authors[0].pk]
        )
        assert (
            list(candidates[0].authors.values_list('pk', flat=True))
            == list(candidates[1].authors.values_list('pk', flat=True))
            == list(candidates[2].authors.values_list('pk', flat=True))
            == [authors[0].pk]
        )

    @pytest.mark.parametrize(['original', 'normalized'], QUOTES_STRS)
    def test_remove_unpaired_quotes(self, original, normalized):
        assert remove_unpaired_quotes(original) == normalized

    @pytest.mark.parametrize(['original', 'normalized'], NORMALIZATION_STRS)
    def test_normalize_name(self, original, normalized):
        assert normalize_name(original) == normalized


@pytest.mark.django_db
class TestUpdateETStaticScores:
    def test_update_static_scores(self, works, authors, candidate):
        for i, (work, author) in enumerate(zip(works, authors)):
            work.authors.add(author)
            for yr in YEARS:
                WorkHit.objects.create(work=work, date=date(yr, 1, 1), value=5 * (i + 1))
        works[1].authors.add(authors[-1])
        candidate.authors.add(*authors)
        update_static_scores(works[0].work_set)
        assert Author.objects.get(pk=authors[0].pk).static_score == {
            'score_2020': 5,
            'score_2015': 10,
            'score_2010': 15,
            'score_2005': 20,
            'score_2000': 25,
            'score_all': 25,
        }
        assert Author.objects.get(pk=authors[-1].pk).static_score == {
            'score_2020': 25,
            'score_2015': 50,
            'score_2010': 75,
            'score_2005': 100,
            'score_2000': 125,
            'score_all': 125,
        }
        assert Author.objects.get(pk=authors[0].pk).normalized_score == {
            'score_2020': 20,
            'score_2015': 20,
            'score_2010': 20,
            'score_2005': 20,
            'score_2000': 20,
            'score_all': 20,
        }


@pytest.mark.django_db()
class TestUpdateAcquisitionScore:
    def test_command(self, works):
        works[0].catalog_date = date(2018, 1, 1)
        works[1].catalog_date = date(2019, 1, 1)
        works[2].catalog_date = date(2020, 1, 1)
        Work.objects.bulk_update(works, ['catalog_date'])
        WorkHit.objects.create(work=works[1], date=date(2019, 2, 2), value=4)
        WorkHit.objects.create(work=works[2], date=date(2020, 2, 2), value=8)
        call_command('update_acquisition_score', works[0].work_set.name)
        assert list(
            Work.objects.order_by('acquisition_score').values_list('acquisition_score', flat=True)
        ) == [0, 4, 8]


@pytest.mark.django_db
class TestSyncWorksWithAleph:
    def test_simple(self):
        AlephEntry.objects.create(
            uid='123456789',
            raw_data={"lang": "cze", "title": [{"a": "Foo bar baz"}], "catalog_date": "170305"},
        )
        assert Work.objects.count() == 0
        call_command('sync_works_with_aleph', 'test')
        assert Work.objects.count() == 1


@pytest.mark.django_db
class TestUpdateGrowthFields:
    @pytest.mark.parametrize(
        ['hits', 'score_past_yr', 'score_yr_b4'],
        [
            ([(500, 1), (400, 2), (300, 3), (200, 5), (100, 7)], 15, 3),  # standard
            ([(500, 1), (400, 2), (380, 3)], 0, 6),  # no usage this year
            ([(1000, 1), (300, 3), (200, 5), (100, 7)], 15, 0),  # no usage last year, some old
            ([(1000, 1), (1100, 2)], 0, 0),  # only very old usage
        ],
    )
    def test_update_growth_fields(self, hits, score_past_yr, score_yr_b4):
        work = WorkFactory.create()
        today = now().date()
        # create data - last year 1+2 = 3, this year 3+5+7 = 15
        for days_back, value in hits:
            WorkHitFactory.create(date=today - timedelta(days=days_back), value=value, work=work)
        assert work.score_past_yr == 0
        assert work.score_yr_b4 == 0
        assert work.absolute_growth == 0
        # check on-the-fly annotation
        work_annot = Work.objects.annotate_absolute_growth().get(pk=work.pk)
        assert work_annot.annotated_absolute_growth == score_past_yr - score_yr_b4
        # call the management command
        call_command('update_growth_fields')
        # check that the values are properly "materialized"
        work.refresh_from_db()
        assert work.score_past_yr == score_past_yr
        assert work.score_yr_b4 == score_yr_b4
        assert work.absolute_growth == score_past_yr - score_yr_b4
        if score_yr_b4:
            assert work.relative_growth == (score_past_yr - score_yr_b4) / score_yr_b4
        else:
            assert work.relative_growth is None


@pytest.mark.django_db
class TestExtractExplicitTopics:
    def test_extract_explicit_topics(self, settings):
        settings.WORK_CATEGORY_EXTRACTOR = 'marc_work_category'
        AlephEntry.objects.create(
            uid='123456789',
            raw_data={
                "lang": "cze",
                "title": [{"a": "Foo bar baz"}],
                "author": [{"a": "Franta"}],
                "contrib": [{"a": "Pepa"}],
                "pub": [{"a": "Hogwarts publishing"}, {"b": "Invalid publisher"}],
                "catalog_date": "170305",
                "konspekt": [
                    {"a": "579", "x": "Mikrobiologie", "2": "Konspekt"},
                    {"a": "Not konspekt"},
                ],
                "lib_info": [{"a": "ABBA 007", "b": "G1234"}],  # G = Disertace
                "cat": [{"2": "psh", "7": "psh826", "a": "mikrobiologie"}],
            },
        )
        work_set, _ = WorkSet.objects.get_or_create(name="test")
        assert Work.objects.count() == 0
        call_command('sync_works_with_aleph', 'test')
        assert Work.objects.count() == 1
        work = Work.objects.get()
        assert work.lang.name == 'cze'
        assert work.authors.count() == 0
        assert work.publishers.count() == 0
        assert work.subject_categories.count() == 0
        assert work.category is None
        assert work.owner_institution is None
        call_command('make_konspekt_tree', 'test')
        # psh is a controlled dictionary, so we must create the categories upfront
        psh_root, _ = SubjectCategory.objects.get_or_create(
            uid='PSH-ROOT', parent=None, work_set=work_set
        )
        SubjectCategory.objects.create(
            uid='PSH826', name='mikrobiologie', parent=psh_root, work_set=work_set
        )
        call_command('extract_explicit_topics', 'test')
        assert work.authors.count() == 2
        assert work.publishers.count() == 1
        work.refresh_from_db()
        assert work.category.name == 'Disertace'
        assert work.owner_institution.name == 'ABBA 007'
        assert work.subject_categories.count() == 1, "just PSH"
        call_command('categorize_works_by_konspekt', 'test')
        assert work.subject_categories.count() == 2, "PSH and Konspekt"
