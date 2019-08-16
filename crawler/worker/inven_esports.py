""":mod:`crawler.worker.ruliweb` ---  Crawler for Ruliweb
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import logging
import re

from .base import BaseSite
from ..exc import SkipCrawler
from ..serializers import payload_serializer

logger = logging.getLogger(__name__)


class InvenEsports(BaseSite):

    def __init__(self, *, threshold=15, page_max=20):
        BaseSite.__init__(self)
        self.threshold = threshold
        self.pageMax = page_max

    def crawler(self):
        log = logger.getChild('InvenEsports.crawler')
        for page in range(1, self.pageMax + 1, 1):
            host = 'http://www.inven.co.kr/webzine/news/'
            query = 'iskin=esports&page={}'.format(page)
            self.url = '{host}?{query}'.format(host=host, query=query)
            soup = self.crawling(self.url)
            if soup is None:
                log.error('{} crawler skip'.format(self.type))
                raise SkipCrawler
            yield soup

    def do(self):
        log = logger.getChild('InvenEsports.do')
        log.info('start {} crawler'.format(self.type))
        for soup in self.crawler():
            for ctx in soup.select('tbody tr'):
                _temp = ctx.span.find_all('span')
                if len(_temp) < 2:
                    continue
                    
                _count = int(re.findall("\d+", _temp[1].text)[0])
                if _count >= self.threshold:
                    _title = ctx.select('a')[0].text
                    _link = ctx.select('a')[0].get('href')
                    obj = payload_serializer(type=self.type, link=_link, count=_count, title=_title)
                    self.insert_or_update(obj)
