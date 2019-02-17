""":mod:`crawler.worker.base` ---  Crawler Base
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import logging

from urllib.error import URLError
from urllib.request import Request, urlopen
from datetime import date, timedelta, datetime, timezone

from bs4 import BeautifulSoup

import sys
sys.path.append("..")

from ..config import crawler_config
from ..database import MongoDB

logger = logging.getLogger(__name__)


class BaseSite:

    def __init__(self):
        if crawler_config.debug:
            self.db = MongoDB('test_crawler')
        else:
            self.db = MongoDB('community_crawler')

        self.url = ""

    @property
    def type(self):
        return self.__class__.__name__

    def insert_or_update(self, data):
        log = logger.getChild(self.type + 'insert_or_update')
        log.setLevel(logging.INFO)

        log.debug('insert data: {}'.format(data))
        collection = 'archive'

        document = None
        objectId = None
        if data.get('id') is None:
            document = self.db.query(collection).find_one({'type': data['type'], 'link': data['link']})
        else:
            document = self.db.query(collection).find_one({'type': data['type'], 'id': data['id']})
                
        if document is None:
            document_by_title = self.db.query(collection).find_one({'type': data['type'], 'title': data['title']})
            if document_by_title is not None:
                limit = datetime.now() - timedelta(hours = 1)
                document_date = document_by_title['date']
                if document_date < limit:
                    return None

            self.db.insert(collection, data=data)
            log.debug('insert data: {}'.format(data))
        else:
            if int(document['count']) < int(data['count']):
                log.debug('update objid: {}, count {}->{}'.format(document['_id'], document['count'], data['count']))
                d = {'count': data['count'], 'update': data['date'], 'title': data['title']}
                objectId = self.db.update(collection, document=document, data=d)
                if objectId['ok']:
                    return document['_id']
                
        return objectId

    def crawling(self, url, encoding='utf-8'):
        log = logger.getChild(self.type + 'crawling')
        request = Request(url, headers={
            'User-Agent':
                'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) '
                'Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1'})
        try:
            handle = urlopen(request)
        except URLError:
            log.error('may be, url host changed: {}'.format(url))
            return None
        data = handle.read()
        soup = BeautifulSoup(data.decode(encoding, 'ignore'), "html.parser", from_encoding="iso-8859-1")

        return soup
