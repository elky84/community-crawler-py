""":mod:`crawler.serve` ---  Crawler thread context
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import logging
import logging.config
import random
import threading
import sys
import os

from datetime import datetime, timedelta

from queue import Queue

from crawler.config import crawler_config
from crawler.exc import SkipCrawler, TerminatedCrawler

from crawler.worker.clien import Clien
from crawler.worker.ppomppu import Ppomppu
from crawler.worker.slrclub import Slrclub
from crawler.worker.todayhumor import Todayhumor
from crawler.worker.thisisgame_pad import ThisisgamePad
from crawler.worker.fmkorea import FmKorea
from crawler.worker.inven_esports import InvenEsports

from crawler.worker.ruliweb_humor import RuliwebHumor
from crawler.worker.ruliweb_hobby import RuliwebHobby
from crawler.worker.ruliweb_hotdeal import RuliwebHotdeal
from crawler.worker.ruliweb_console_news import RuliwebConsoleNews
from crawler.worker.ruliweb_pc_news import RuliwebPcNews

from pymongo.errors import ServerSelectionTimeoutError
from time import sleep

logger = logging.getLogger('crawler')
logging.config.dictConfig(crawler_config.logging_formatter)


class Crawler(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        l = logger.getChild('Crawler.run')
        site = self.queue.get()
        
        while True:
            try:
                site.do()
            except ServerSelectionTimeoutError:
                l.info('ServerSelectionTimeoutError')
            except SkipCrawler:
                l.info('SkipCrawler')
            except Exception as e: 
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                l.error(e)
                l.error(exc_type, fname, exc_tb.tb_lineno)

            sleep(int(crawler_config.crawler_interval['sec']))

        self.queue.task_done()


def crawler(*, queue: Queue):
    sites = [
        Clien(threshold=500, page_max=10),
        Ppomppu(threshold=500, page_max=10),
        Slrclub(threshold=500, page_max=10),
        Todayhumor(threshold=500, page_max=10),
        RuliwebHobby(threshold=500, page_max=10),
        RuliwebHumor(threshold=500, page_max=10),
        RuliwebConsoleNews(threshold=100, page_max=3),
        RuliwebPcNews(threshold=100, page_max=3),
        RuliwebHotdeal(threshold=0, page_max=3),
        ThisisgamePad(threshold=0, page_max=3),
        FmKorea(threshold=0, page_max=1),
        InvenEsports(threshold=0, page_max=3),
    ]
    thread_num = len(sites)
    for site in sites:
        queue.put(site)
    workers = []
    for i in range(thread_num):
        t = Crawler(queue)
        t.daemon = True
        workers.append(t)
        t.start()
    return workers


if __name__ == '__main__':
    l = logger.getChild('main')
    oldtime = datetime.now()
    l.info('crawler start')
    count = 0
    queue = Queue()
    while True:
        try:
            interval = crawler_config.crawler_interval
            seed = timedelta(minutes=random.randint(
                int(interval['minutes_min']), int(interval['minutes_max'])),
                seconds=int(interval['sec']))
            if datetime.now() >= (oldtime + seed):
                oldtime = datetime.now()
                workers = crawler(queue=queue)
                queue.join()
                count += 1
                l.info("finish crawler: {}".format(count))
        except (KeyboardInterrupt, TerminatedCrawler):
            l.info('terminated crawler')
            exit()
        except Exception as e:
            l.info('exception catched. {}'.format(e))
