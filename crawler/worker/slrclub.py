""":mod:`crawler.worker.slrclub` ---  Crawler for Slrclub
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import logging

from .base import BaseSite
from ..exc import SkipCrawler
from ..serializers import payload_serializer

logger = logging.getLogger(__name__)


class Slrclub(BaseSite):

    def __init__(self, *, threshold=15, page_max=20):
        BaseSite.__init__(self)
        self.threshold = threshold
        self.pageMax = page_max

    def crawler(self):
        log = logger.getChild('Slrclub.crawler')
        url = 'http://www.slrclub.com/bbs/zboard.php?id=free'
        soup = self.crawling(url)
        if soup is None:
            log.error('{} crawler skip'.format(self.type))
            raise SkipCrawler

        bbs_foot = soup.select('table#bbs_foot')[0]
        tr = bbs_foot.select('tr')
        list_num = tr[1].select('td')
        a = list_num[0].select('a')
        pageCount = int(a[11].get('href').split('page=')[1])

        for page in range(1, self.pageMax + 1, 1):
            host = 'http://www.slrclub.com/bbs/zboard.php'
            query = 'id=free&page={}'.format(pageCount - page + 1)
            self.url = '{host}?{query}'.format(host=host, query=query)
            soup = self.crawling(self.url)
            if soup is None:
                log.error('{} crawler skip'.format(self.type))
                raise SkipCrawler
            yield soup

    def do(self):
        log = logger.getChild('Slrclub.do')
        log.info('start {} crawler'.format(self.type))
        for soup in self.crawler():
            for ctx in soup.select('table#bbs_list tbody tr'):
                if ctx.select('td.list_num'):
                    text = ctx.a.extract()
                    _temp = ctx.select('td.list_click.no_att')[0].text.strip()
                    if _temp == '':
                        continue

                    _count = int(_temp)
                    if _count >= self.threshold:
                        _id = text.get('href').split('no=')[1]
                        _title = text.text
                        _link = self.url.split('/bbs')[0] + text.get('href')
                        obj = payload_serializer(type=self.type, id=_id, link=_link, count=_count, title=_title)
                        self.insert_or_update(obj)