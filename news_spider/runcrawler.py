import logging
import sys
import os
import traceback
from daemon import Daemon, daemon_main

from news_spider.spider import NewsCrawler
from news_spider.settings import _LOGGER, START_DATE, END_DATE,\
        BASE_ROLLPAGE, SITE, MODE

def news_crawler():
    try:
        newsCrawler = NewsCrawler(BASE_ROLLPAGE, SITE, START_DATE, END_DATE)
        newsCrawler.news_crawler(MODE)
    except Exception, err:
        _LOGGER.error(err)
        _LOGGER.error("%s" % traceback.format_exc())

class CrawlerDaemon(Daemon):
    '''
    Crawler daemon process to run linkcrawler
    '''

    def __init__(self, pidfile, stdin=os.devnull, stdout=os.devnull, stderr=os.devnull):
        Daemon.__init__(self, pidfile, stdin, stdout, stderr)

    def run(self):
        news_crawler()

if __name__ == "__main__":
    daemon_main(CrawlerDaemon, '/var/run/news_spider.pid', sys.argv)

