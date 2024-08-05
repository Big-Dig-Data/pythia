import pytest

from ..logic.topics import marc_author_topics, marc_subject_topics


@pytest.mark.django_db()
class TestTopicExtraction(object):
    def test_marc_author_topics(self, works):
        assert marc_author_topics(works[0]) == [("Tuček, Jan", None, 1.0)]

    def test_marc_subject_topics(self, works):
        subjects1 = marc_subject_topics(works[0])
        assert len(subjects1) == 2, "no psh stuff, it is handled in a separate function"
        assert subjects1[0] == ("629.331(091)", 'MRF', 1.0)
