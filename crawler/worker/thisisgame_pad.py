""":mod:`crawler.worker.ruliweb` ---  Crawler for Ruliweb
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import logging

from .base import BaseSite
from ..exc import SkipCrawler
from ..serializers import payload_serializer

logger = logging.getLogger(__name__)


class ThisisgamePad(BaseSite):

    def __init__(self, *, threshold=15, page_max=20):
        BaseSite.__init__(self)
        self.threshold = threshold
        self.pageMax = page_max

    def crawler(self):
        log = logger.getChild('ThisisgamePad.crawler')
        for page in range(1, self.pageMax + 1, 1):
            self.host = 'https://www.thisisgame.com/pad/tboard/?board=21'
            query = 'page&page={}'.format(page)
            self.url = '{host}?{query}'.format(host=self.host, query=query)
            soup = self.crawling(self.url)
            if soup is None:
                log.error('{} crawler skip'.format(self.type))
                raise SkipCrawler
            yield soup

    def do(self):
        log = logger.getChild('ThisisgamePad.do')
        log.info('start {} crawler'.format(self.type))
        for soup in self.crawler():
            tr = soup.select('tr')
            for ctx in tr:
                if len(ctx.attrs) <= 0 or ctx.attrs.get('class') == None:
                    continue

                tr_class = ctx.attrs['class']
                if 1 <= len(tr_class) and tr_class[0] == "notice":
                    continue

                _temp = ctx.select("td.number")
                if len(_temp) < 2:
                    continue
                    
                _count = int(_temp[1].text.replace("\n", ""))
                if _count >= self.threshold:
                    _title = ctx.select('a')[0].text
                    _link = self.host + ctx.select('a')[0].get('href')
                    obj = payload_serializer(type=self.type, link=_link, count=_count, title=_title)
                    self.insert_or_update(obj)
