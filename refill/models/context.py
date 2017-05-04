from concurrent.futures import ThreadPoolExecutor
from importlib import import_module
import celery.utils.log
import logging


class Context:
    def __init__(self):
        """Initialize the context

        Note:
            This does not depend on Celery. If no Celery task is attached,
            Celery-related methods are noop.
        """
        self._task = None
        self._page = None

        self.transforms = []
        self.transformMetadata = {}
        self.currentTransform = None
        self.currentTransformIndex = 0
        self.wikicode = None
        self.origWikicode = ''

        self.executor = ThreadPoolExecutor(max_workers=10)
        self.getLogger = logging.getLogger
        self.logging = self.getLogger('refill')

    def attachTask(self, task):
        """Attach a Celery Task object
        """
        self._task = task
        self.getLogger = celery.utils.log.get_logger
        self.logging = self.getLogger('refill')

    def attachPage(self, page):
        """Attach a pywikibot page
        """
        self._page = page

    def applyTransforms(self, wikicode):
        """Apply scheduled transforms on the wikicode
        """
        self.wikicode = wikicode
        self.origWikicode = str(wikicode)
        for index, transform in enumerate(self.transforms):
            self.currentTransform = transform
            self.currentTransformIndex = index
            self._updateState()
            transform.apply(wikicode)

    def getResult(self):
        """Get the final result as Celery metadata
        """
        return self._generateTaskMetadata()

    def getPage(self):
        """Get the associated pywikibot Page object
        """
        if self._page:
            return self._page
        return False

    def reportProgress(self, state: str, percentage: float, metadata: dict):
        """Report progress of the current transform
        """
        name = self.currentTransform.__class__.__name__
        self.transformMetadata[name] = {
            'state': state,
            'percentage': percentage,
            'metadata': metadata,
        }
        self._updateState()

    def _updateState(self):
        """Actually send our state to Celery
        """
        if self._task:
            self._task.update_state(state='PROGRESS', meta=self._generateTaskMetadata())

    def _generateTaskMetadata(self):
        """Generate task metadata for Celery
        """
        # Generate percentage
        name = self.currentTransform.__class__.__name__
        ind = self.currentTransformIndex
        if name in self.transformMetadata and \
           'percentage' in self.transformMetadata[name]:
            ind += self.transformMetadata[name]['percentage']
        percentage = ind / len(self.transforms)

        # Generate partial wikicode
        wikicode = str(self.wikicode) if self.wikicode else ''

        # Generate wiki page information
        if self._page:
            site = self._page.site
            family = site.family
            wikipage = {
                'fam': family.name,
                'code': site.code,
                'lang': site.lang,
                'page': self._page.title(),
                'upage': self._page.title(underscore=True),
                'domain': site.hostname(),
                'path': site.path(),
                'protocol': site.protocol(),
                'editTime': self._page.editTime().totimestampformat(),
                'startTime': site.getcurrenttime().totimestampformat(),
            }
        else:
            wikipage = {}

        return {
            'overall': {
                'percentage': percentage,
                'currentTransform': self.currentTransform.__class__.__name__,
                'currentTransformIndex': self.currentTransformIndex,
                'totalTransforms': len(self.transforms),
            },
            'transforms': self.transformMetadata,
            'wikicode': wikicode,
            'origWikicode': self.origWikicode,
            'wikipage': wikipage,
        }
