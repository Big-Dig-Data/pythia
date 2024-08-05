import requests


class GoogleBooksAPI(object):

    URL_BASE = 'https://www.googleapis.com/books/v1/volumes'

    def __init__(self, api_key=None):
        self.session = requests.Session()
        self.api_key = api_key

    @staticmethod
    def clean_isbn(isbn: str) -> str:
        return isbn.strip().replace("-", "")

    def get_info_by_isbn(self, isbn: str) -> dict:
        params = {'q': 'isbn:{}'.format(self.clean_isbn(isbn))}
        if self.api_key:
            params['key'] = self.api_key
        result = self.session.get(self.URL_BASE, params=params)
        return result.json()
