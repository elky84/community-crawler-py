""":mod:`crawler.worker.clien` ---  Crawler for Clien
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import logging

from .base import BaseSite
from ..exc import SkipCrawler
from ..serializers import payload_serializer

logger = logging.getLogger(__name__)


class Clien(BaseSite):

    def __init__(self, *, threshold=20, page_max=20):
        BaseSite.__init__(self)
        self.threshold = threshold
        self.page_max = page_max
        self.article_base_url = 'https://www.clien.net'

    def crawler(self):
        log = logger.getChild('Clien.crawler')
        for page in range(1, self.pageMax + 1, 1):
            host = 'http://clien.net/service/board/park'
            query = 'od=T31&po={}'.format(page)
            self.url = '{host}?{query}'.format(host=host, query=query)
            soup = self.crawling(self.url)
            if soup is None:
                log.error('{} crawler skip'.format(self.type))
                raise SkipCrawler
            yield soup

    def do(self):
        log = logger.getChild('Clien.do')
        log.info('start {} crawler'.format(self.type))
        for soup in self.crawler():
            # https://github.com/liza183/clienBBS/blob/master/clien.py 
            # 맨 끝에 space 2개... 클리앙...
            for ctx in soup.find_all('div', {"class": 'list_item symph_row  '}):
                _count = ctx.findAll("div")[3].span.text # 문자열 축약 처리가 있어 바로 int 캐스팅 못하고, 축약 검사.
                if ' k' in _count: # 더 많은 히트수가 있을 수 있으나, k로만 축약했다는 가정...흠...
                    _count = int(float(_count.replace(" k", "")) * 1000)
                else:
                    _count = int(_count)
                
                if _count >= self.threshold:
                    _title = ctx.find("div",{"class":"list_title"}).span.text
                    _link = self.article_base_url + ctx.find("a",{"class":"list_subject"})['href'].split('?')[0] # 쿼리파라미터 제거
                    _author = ctx['data-author-id'].strip()
                    _timestamp = ctx.find("div",{"class":"list_time"}).span.span.text
                        
                    obj = payload_serializer(type=self.type, link=_link, count=_count, title=_title)
                    self.insert_or_update(obj)
