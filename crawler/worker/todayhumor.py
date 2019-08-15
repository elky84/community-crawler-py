""":mod:`crawler.worker.todayhumor` ---  Crawler for TodayHumor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import logging

from .base import BaseSite
from ..exc import SkipCrawler
from ..serializers import payload_serializer
import re

logger = logging.getLogger(__name__)


class Todayhumor(BaseSite):

    def __init__(self, *, threshold=100, page_max=5):
        BaseSite.__init__(self)
        self.threshold = threshold
        self.pageMax = page_max

    def crawler(self):
        log = logger.getChild('Todayhumor.crawler')
        for page in range(1, self.pageMax + 1, 1):
            host = 'http://www.todayhumor.co.kr/board/list.php'
            query = 'table=bestofbest&page={}'.format(page)
            self.url = '{host}?{query}'.format(host=host, query=query)
            soup = self.crawling(self.url)
            if soup is None:
                log.error('{} crawler skip'.format(self.type))
                raise SkipCrawler
            yield soup

    def do(self):
        log = logger.getChild('Todayhumor.do')
        log.info('start {} crawler'.format(self.type))
        for soup in self.crawler():
            for ctx in soup.select('tbody tr'):
                _temp = ctx.select('td.hits')
                if len(_temp) <= 0:
                    continue

                _subject = ctx.select('td.subject')[0]
                _count = int(_temp[0].text)
                if _count >= self.threshold:
                    _id = _subject.select('a')[0].get('href').split('s_no=')[1].split('&page')[0]
                    _title = _subject.select('a')[0].text
                    _link = re.sub("&page=[0-9]", "", self.url.split('/board/list.php')[0] + _subject.select('a')[0].get('href'))
                    obj = payload_serializer(type=self.type, id=_id, link=_link, count=_count, title=_title)
                    self.insert_or_update(obj)
