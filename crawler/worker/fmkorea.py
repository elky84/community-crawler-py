""":mod:`crawler.worker.ruliweb` ---  Crawler for Ruliweb
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import logging

from .base import BaseSite
from ..exc import SkipCrawler
from ..serializers import payload_serializer

logger = logging.getLogger(__name__)


class FmKorea(BaseSite):

    def __init__(self, *, threshold=15, page_max=20):
        BaseSite.__init__(self)
        self.threshold = threshold
        self.pageMax = page_max

    def crawler(self):
        log = logger.getChild('FmKorea.crawler')
        for page in range(1, self.pageMax, 1):
            host = 'https://www.fmkorea.com/index.php'
            query = 'mid=football_news&page={}'.format(page)
            self.url = '{host}?{query}'.format(host=host, query=query)
            soup = self.crawling(self.url)
            if soup is None:
                log.error('{} crawler skip'.format(self.type))
                raise SkipCrawler
            yield soup

    def do(self):
        log = logger.getChild('FmKorea.do')
        log.info('start {} crawler'.format(self.type))
        for soup in self.crawler():
            for ctx in soup.select('tbody tr'):
                _temp = ctx.select("td.m_no")
                if len(_temp) < 2:
                    continue

                text = _temp[1].text.replace("\t", "")
                if text == "\xa0":
                    continue
                
                _count = int(text)
                if _count >= self.threshold:
                    _title = ctx.select('a')[1].text.replace("\t", "")
                    _link = self.url.split('/index.php')[0] + ctx.select('a')[1].get('href')
                    obj = payload_serializer(type=self.type, link=_link, count=_count, title=_title)
                    self.insert_or_update(obj)
