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
        self.db = MongoDB(crawler_config.db_name)
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
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36)'})
        try:
            handle = urlopen(request, timeout=10)
        except URLError:
            log.error('may be, url host changed: {}'.format(url))
            return None
        except TimeoutError:
            log.error('urlopen timeout: {}'.format(url))
            return None
        except Exception as e:
            log.error('urlopen exception raised. {} {}'.format(url, e))
            return None
            
        if handle.status != 200:
            log.error('http status is not 200. {} {}'.format(url, handle.status))
            return None

        try:
            data = handle.read()
            soup = BeautifulSoup(data.decode(encoding, 'ignore'), "html.parser", from_encoding="iso-8859-1")
            # log.debug('soup text: {}'.format(soup.text))
            return soup
        except Exception as e:
            log.error('handle.read() or BeautifulSoup exception raised. {} {}'.format(url, e))
            return None

