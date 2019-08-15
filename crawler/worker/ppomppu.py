""":mod:`crawler.worker.ppomppu` ---  Crawler for Ppomppu
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import logging
import re

from .base import BaseSite
from ..exc import SkipCrawler
from ..serializers import payload_serializer

logger = logging.getLogger(__name__)


class Ppomppu(BaseSite):

    def __init__(self, *, threshold=30, page_max=20):
        BaseSite.__init__(self)
        self.threshold = threshold
        self.pageMax = page_max

    def crawler(self):
        log = logger.getChild('Ppomppu.crawler')
        for page in range(1, self.pageMax + 1, 1):
            host = 'http://www.ppomppu.co.kr/zboard/zboard.php'
            query = 'id=freeboard&page={}'.format(page)
            self.url = '{host}?{query}'.format(host=host, query=query)
            soup = self.crawling(self.url, encoding='euc-kr')
            if soup is None:
                log.error('{} crawler skip'.format(self.type))
                raise SkipCrawler
            yield soup

    def do(self):
        log = logger.getChild('Ppomppu.do')
        log.info('start {} crawler'.format(self.type))
        for soup in self.crawler():
            for ctx in soup.select('table#revolution_main_table tr'):
                if ctx.get('class') is not None and bool(re.match('list(0|1)', ctx.get('class')[0])):
                    _count = int(ctx.select('td.eng.list_vspace')[3].text)
                    
                    if _count >= self.threshold:
                        _id = ctx.select('a')[1].get('href').split('no=')[1]
                        _title = ctx.select('a')[1].text
                        _link = self.url.split('zboard.php')[0] + ctx.select('a')[1].get('href')
                        obj = payload_serializer(type=self.type, id=_id, link=_link, count=_count, title=_title)
                        self.insert_or_update(obj)
