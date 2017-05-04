import requests
import re
from furl import furl
from ..models import Citation
from bs4 import BeautifulSoup


class NotFoundError(Exception):
    def __init__(self, url):
        super().__init__(url)


class UnknownError(Exception):
    def __init__(self, url):
        super().__init__(url)


class Standalone:
    def __init__(self):
        pass

    def fetch(self, url: str):
        citation = Citation()
        parsedUrl = furl(url)

        if not parsedUrl.scheme:
            return

        response = requests.get(url)
        if response.status_code == 404:
            raise NotFoundError(url)
        elif response.status_code != 200:
            raise UnknownError(url)

        soup = BeautifulSoup(response.text, 'html.parser')

        parsers = [
            self._parse_title,
            self._parse_archiveis
        ]
        for parser in parsers:
            parser(soup, citation, parsedUrl)

        return citation

    def _parse_archiveis(self, soup, citation, parsedUrl):
        supportedDomains = [
            'archive.is',
            'archive.fo',
            'archive.li',
            'archive.today',
        ]
        if parsedUrl.netloc not in supportedDomains:
            return

        node = soup.find(id='SHARE_LONGLINK')
        if node:
            archiveurl = furl(node['value'])
            archiveurl.protocol = 'https'
            archiveurl.path.segments[0] = re.sub(
                r'^(\d{4})\.(\d{2})\.(\d{2})\-(\d{6})$', '\\1\\2\\3\\4',
                archiveurl.path.segments[0])
            origOffset = str(archiveurl.path).find('/', 1) + 1
            origUrl = str(archiveurl.path)[origOffset:]
            citation.archiveurl = archiveurl.url
            citation.url = origUrl

    def _parse_title(self, soup, citation, parsedUrl):
        node = soup.title
        if node:
            citation.title = str(node.string)
