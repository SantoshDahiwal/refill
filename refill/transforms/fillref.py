import re

from .transform import Transform
from ..formatters import CiteTemplate
from ..fetchers import Citoid, Standalone
from ..models import Citation
from ..utils import Parser

from concurrent.futures import as_completed
from urllib.parse import urlparse


class NoTitleError(Exception):
    pass


class FillRef(Transform):
    def __init__(self, ctx=None):
        super().__init__(ctx)
        self.fetchers = [
            Citoid(),
            (r'^archive\.(is|fo|li|today)', Standalone()),
        ]
        self.formatter = CiteTemplate()

    def apply(self, wikicode):
        tags = wikicode.filter_tags()

        futures = set()

        refCount = 0
        completeCount = 0
        errors = []

        self._ctx.reportProgress('SCANNING', 0, {})
        for tag in tags:
            if tag.tag != 'ref' or tag.self_closing or not tag.contents:
                continue

            citation = Parser.parse(tag.contents)
            if not citation:
                continue

            refCount += 1

            futures.add(self._ctx.executor.submit(self._fulfill, citation, tag))

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                errors.append(str(e))
            else:
                completeCount += 1

            self._ctx.reportProgress('FETCHING', completeCount / refCount, {
                'count': completeCount,
                'errors': errors
            })

        if not errors:
            linkrot_templates = [
                'bare',
                'bare links',
                'barelinks',
                'bare url',
                'bare references',
                'bare refs',
                'bare urls',
                'cleanup link rot',
                'cleanup link-rot',
                'cleanup-link-rot',
                'cleanup-linkrot',
                'link rot',
                'linkrot',
                'cleanup-bare urls',
            ]
            for template in wikicode.ifilter_templates():
                if template.name.lower() in linkrot_templates:
                    wikicode.remove(template)

        return wikicode

    def _fulfill(self, citation, tag):
        url = citation.url
        err = None

        c, err = self._fetch(url)
        citation.merge(c)

        if 'archiveurl' in citation:
            c, _ = self._fetch(citation.archiveurl)
            if c.url not in [citation.url, citation.archiveurl]:
                citation.url = c.url
            if c.archiveurl != citation.archiveurl:
                citation.archiveurl = c.archiveurl

        if 'url' in citation and 'title' in citation:
            tag.contents = self.formatter.format(citation)
        elif err:
            raise err
        else:
            raise NoTitleError()

    def _fetch(self, url):
        err = None
        citation = Citation()

        for f in self.fetchers:
            try:
                if type(f) is tuple:
                    parsed = urlparse(url)
                    if re.match(f[0], parsed.netloc):
                        citation.merge(f[1].fetch(url))
                else:
                    citation.merge(f.fetch(url))
            except Exception as e:
                err = e

        return citation, err
