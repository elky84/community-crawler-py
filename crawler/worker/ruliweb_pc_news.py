""":mod:`crawler.worker.ruliweb` ---  Crawler for Ruliweb
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import logging

from .base import BaseSite
from ..exc import SkipCrawler
from ..serializers import payload_serializer

logger = logging.getLogger(__name__)


class RuliwebPcNews(BaseSite):

    def __init__(self, *, threshold=15, page_max=20):
        BaseSite.__init__(self)
        self.threshold = threshold
        self.pageMax = page_max

    def crawler(self):
        log = logger.getChild('RuliwebPcNews.crawler')
        for page in range(1, self.pageMax + 1, 1):
            host = 'http://bbs.ruliweb.com/news/board/1003'
            query = 'page={}'.format(page)
            self.url = '{host}?{query}'.format(host=host, query=query)
            soup = self.crawling(self.url)
            if soup is None:
                log.error('{} crawler skip'.format(self.type))
                raise SkipCrawler
            yield soup

    def do(self):
        log = logger.getChild('RuliwebPcNews.do')
        log.info('start {} crawler'.format(self.type))
        for soup in self.crawler():
            for ctx in soup.select('tbody tr'):
                _temp = ctx.select("td.hit")
                if len(_temp) == 0 or _temp[0].text == "\n":
                    continue
                    
                _count = int(_temp[0].text.replace("\n", ""))
                if _count >= self.threshold:
                    a_tag = ctx.select('a')
                    _title = '[{category}] {title}'.format(category=a_tag[0].text, title=a_tag[1].text)
                    _link = ctx.select('a')[1].get('href')
                    obj = payload_serializer(type=self.type, link=_link, count=_count, title=_title)
                    self.insert_or_update(obj)
