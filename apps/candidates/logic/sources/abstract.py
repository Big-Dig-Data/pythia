from typing import Generator


class CandidateRec(object):
    """
    Represents one Work Candidate
    """

    def __init__(
        self,
        id_in_source,
        title=None,
        contributors=None,
        lang=None,
        description=None,
        publisher=None,
        isbn=None,
    ):
        self.id_in_source = id_in_source
        self.title = title
        self.contributors = contributors or []
        self.lang = lang
        self.description = description
        self.publisher = publisher
        self.isbn = isbn

    def to_dict(self):
        return {
            'id_in_source': self.id_in_source,
            'title': self.title,
            'description': self.description,
            'contributors': self.contributors,
            'publisher': self.publisher,
            'lang': self.lang,
            'isbn': self.isbn,
        }


class CandidateImporter(object):
    def gen_candidates(self, source: str) -> Generator[dict, None, None]:
        """
        Should generate dictionaries with raw records as extracted from the source
        :param source: path to the source (file, url, etc.)
        :return:
        """
        raise NotImplementedError()

    def raw_to_common(self, raw_data: dict) -> CandidateRec:
        """
        Should convert the raw record as read from the source to the common format
        :param raw_data:
        :return:
        """
        raise NotImplementedError()
