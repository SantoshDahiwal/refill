import mwparserfromhell
from mwparserfromhell.wikicode import Wikicode
from mwparserfromhell.nodes.external_link import ExternalLink
from mwparserfromhell.nodes.template import Template
from ..models import Citation
from . import Utils


class Parser:
    def parse(content: Wikicode):
        if type(content) is str:
            content = mwparserfromhell.parse(content)

        citation = Citation()
        for node in content.ifilter(forcetype=(ExternalLink, Template), recursive=False):
            if type(node) is ExternalLink:
                citation.url = str(node.url)
                if node.title:
                    citation.title = str(node.title)
            elif type(node) is Template:
                tname = Utils.homogenizeTemplateName(str(node.name))
                if tname == 'Cite web' and \
                   not node.has('title') and \
                   node.has('url'):
                    citation.url = str(node.get('url').value)
                elif tname == 'Webarchive':
                    if node.has('url'):
                        citation.archiveurl = str(node.get('url').value)
                    if node.has('date'):
                        citation.archivedate = str(node.get('date').value)
                    if node.has('title'):
                        citation.title = str(node.get('title').value)

        if 'url' in citation:
            return citation
        return False
