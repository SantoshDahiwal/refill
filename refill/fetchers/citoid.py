import requests
from urllib.parse import unquote, quote_plus
from ..models import Citation


class NotFoundError(Exception):
    def __init__(self, url):
        super().__init__(url)


class UnknownError(Exception):
    def __init__(self, url):
        super().__init__(url)


class Citoid:
    ENDPOINT = 'https://en.wikipedia.org/api/rest_v1/data/citation'
    MAPPING = {
        'default': {
            'url': 'url',
            'title': 'title',
            'author': 'authors',
            'editor': 'editors',
            'publisher': 'publisher',
            'date': 'date',
            'volume': 'volume',
            'issue': 'issue',
            'pages': 'pages',
            'PMID': 'pmid',
            'PMCID': 'pmc',
            'DOI': 'doi',
            'libraryCatalog': 'via',
            'websiteTitle': 'website',
        },
        'bookSection': {
            'bookTitle': 'title',
        },
        'journalArticle': {
            'publicationTitle': 'journal',
        },
    }

    def __init__(self):
        pass

    def fetch(self, url: str):
        citation = Citation()

        action = Citoid.ENDPOINT + "/mediawiki/"
        action += quote_plus(unquote(url))

        response = requests.get(action)
        if response.status_code == 404:
            raise NotFoundError(url)
        elif response.status_code != 200:
            raise UnknownError(url)

        data = response.json()[0]
        citation.type = data['itemType']

        mapping = Citoid.MAPPING['default'].copy()
        if citation.type in Citoid.MAPPING:
            mapping.update(Citoid.MAPPING[citation.type])

        for cfield, value in data.items():
            if cfield in mapping:
                field = mapping[cfield]
                citation[field] = value

        if citation.url == citation.title:
            citation.title = ''

        return citation
