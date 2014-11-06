#!/usr/bin/env python
#coding=utf-8
"""
Created on Sep 1, 2014
@Author: Zixuan Zhang

@Des: This script provides basic news crawler function

"""

import re
import time
import json
import logging
import urllib
import urllib2
import datetime
from lxml import html

import pymongo

import newsdb

# log format config
FORMAT = '%(asctime)s %(levelname)s %(name)s %(message)s'
logging.basicConfig(filename = 'log', level = logging.INFO, format = FORMAT)
_LOGGER = logging.getLogger()

ROLL_PAGE = [{"SINA": "http://roll.sports.sina.com.cn/s/channel.php?ch=02#col=64&date=%s&ch=02&offset_page=0&offset_num=0&num=10000&page=1"}
        ]
CMNT_BASE_URL = "http://comment5.news.sina.com.cn/page/info?format=js&jsvar=pagedata&channel=ty&newsid=%s&group=0&page=1&list=all&fr=ct"

class NewsCrawler():
    """
    Crawler Class
    """

    def __init__(self, basicUrl, site, startDate, endDate, interval=2):
        """
        Initialize NewsCrawler Class
        """
        self.basicUrl = basicUrl
        self.site = site
        self.startDate = startDate;
        self.endDate = endDate;
        self.interval = interval
        self.year = None
        self.month = None
        self.day = None
        self.dateRange = []
        self._date_range(startDate, endDate)

    def _date_range(self, startDate, endDate):
        tmp2 = startDate.split('-')
        tmp1 = endDate.split('-')

        start_time = datetime.datetime(int(tmp2[0]), int(tmp2[1]), int(tmp2[2]))
        end_time   = datetime.datetime(int(tmp1[0]), int(tmp1[1]), int(tmp1[2]))
        for n in range(int((end_time - start_time).days)):
            t = start_time + datetime.timedelta(n)
            self.year = str(t.year)
            if t.month < 10:
                self.month = "0" + str(t.month)
            else:
                self.month = str(t.month)
            if t.day < 10:
                self.day = "0" + str(t.day)
            else:
                self.day = str(t.day)
            date = self.year + "-" + self.month + "-" + self.day
            self.dateRange.append(date)

    def crawl_news_list(self, rollpage):
        """
        Crawl News List From Roll Page
        """
        request = urllib2.Request(rollpage)
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.8.1.14) \
                Gecko/20080404 (FoxPlus) Firefox/2.0.0.14')
        count = 0
        try:
            page = urllib2.urlopen(request).read()
        except Exception, err:
            print "Open Link Error %s %s" % (rollpage,err)
            if count >= 3:
                return []
            count += 1

        content_list = re.findall(r',title[^}]*', page, re.M);
        news_list = []
        for content in content_list:
            items = content.split(',')
            items = items[1:]
            news = {"type" : 0}
            for item in items:
                key = None
                value = None
                try:
                    i = item.split(' : ')
                    key = i[0].strip()
                    value = i[1].strip()
                    value = value.strip('"')
                    value = value.strip("'")
                except IndexError, err:
                    print item
                    break
                if key == "title":
                    value = value.decode('gbk')
                key = key.encode('utf-8')
                value = value.encode('utf-8')
                news[key] = value
            if(news['type'] == "1"):
                news_list.append(news)
                    
        return news_list

    def parse_news_list(self, list_html):
        """
        Parse News List Html To a List of News
        """
        pass

    def save_news_list(self, news_list):
        for news in news_list:
            newsdb.insert_news_link(news)

    def save_news_link(self, newsLink):
        newsdb.insert_news_link(newsLink)

    def save_news(self, news):
        newsdb.insert_news(news)

    def crawl_news(self, news_url):
        """
        Crawl News Content For a Given News Url
        """
        _LOGGER.info("NEWS URL: %s" % news_url)
        count = 0
        try:
            page = urllib.urlopen(news_url).read()
        except Exception, err:
            _LOGGER.error("NEWS_GET_ERROR %s %s" % (news_url, err))
            if count >= 3:
                return False
            count += 1

        _LOGGER.info("PageCrawledSuccess")
        news = self.parse_news(page)
        if not news:
            return False
        news['url'] = news_url
        self.save_news(news)
        return True

    def _get_comment_number(self, comment_id):
        count = 0
        try:
            url = CMNT_BASE_URL % comment_id
            page = urllib.urlopen(url).read()
            data = unicode(page, 'gbk')
            data = data[13:]
            jdata = json.loads(data)
            count = jdata['result']['count']['total']
            return int(count)
        except Exception, err:
            _LOGGER.error("GetCommentNumberError %s" % err)
            return 0

    def _get_commentid_reg(self, page):
        reg = """newsid:[0-9\-'"]+,"""
        pattern = re.compile(reg)
        res = pattern.findall(page)
        newsId = None
        if res:
            res = res[0]
            newsId = res[8:len(res) - 2]
        return newsId

    def parse_news(self, page):
        """
        Parse News Content For a Given News Html
        """
        #TODO: sometimes this code will crash
        try:
            page = page.decode('gbk')
        except UnicodeDecodeError, err:
            _LOGGER.error("DecodePageError %s" % err)
            return False

        dom = html.fromstring(page)
        xpaths = {"title": "//div[@class='blkContainerSblk']/h1[@id='artibodyTitle']//text()",
                "pubDate": "//div[@class='blkContainerSblk']/div[@class='artInfo']/span[@id='pub_date']/text()",
                "text": "//div[@class='blkContainerSblk']/div[@id='artibody']/p/text()",
                "commentId": "//meta[@name='comment']/@content"}

        titles = dom.xpath(xpaths['title'])
        pubDate = dom.xpath(xpaths['pubDate'])
        texts = dom.xpath(xpaths['text'])
        comment = dom.xpath(xpaths['commentId'])

        commentId = ""
        title = ""
        text = ""
        commentNumber = 0

        if comment:
            commentId = comment[0]
            commentId = commentId.split(':')[1]
        else:
            commentId = self._get_commentid_reg(page)
        for t in titles:
            title += t;
        if pubDate:
            pubDate = pubDate[0]
        if texts:
            for t in texts:
                text += t
        textLen = len(text)
        titleLen = len(title)

        if not title:
            _LOGGER.warning("PARSE_FAILED : Title Empty")
            return False

        _LOGGER.info("CommentId %s" % commentId)
        if commentId:
            commentNumber = self._get_comment_number(commentId)

        _LOGGER.info("Title: %s" % title)
        _LOGGER.info("PubDate: %s" % pubDate)
        _LOGGER.info("CommentNumber: %d" % commentNumber)
        #_LOGGER.info("Conent: %s" % text)
        _LOGGER.info("ContentLen: %d" % textLen)

        news = {"title": title,
                "pubDate": pubDate,
                "commentNumber": commentNumber,
                "titleLen": titleLen,
                "textLen": textLen,
                "text": text}
        return news

    def news_crawler(self):
        """
        Class API
        """
        for date in self.dateRange:
            self.crawl_as_date(date)

    def crawl_as_date(self, date):
        """
        Crawl News as Date
        """
        rollPage = self.basicUrl % date
        _LOGGER.info("NEWS_DATE : %s" % date)
        _LOGGER.info("LIST_URL %s" % rollPage)
        newsList = self.crawl_news_list(rollPage)
        _LOGGER.info("NEWS_LIST_CRAWLED LEN : %d" % len(newsList))
        for news in newsList:
            newsUrl = news["url"]
            result = self.crawl_news(newsUrl)
            if result:
                news['crawled'] = True
                self.save_news_link(news)
                _LOGGER.info("CRAWL_NEWS_SUC %s" % newsUrl)
            else:
                _LOGGER.warning("CRAWL_NEWS_FAILED %s" % newsUrl)

def crawl_list_test():
    url = "http://roll.sports.sina.com.cn/interface/rollnews_ch_out_interface.php?col=94&num=10000&date=%s"
    newsCrawler = NewsCrawler(url, "sina", "2012-11-10", "2012-11-16")
    news_list = newsCrawler.news_crawler()

def crawl_news_test():

    url = "http://roll.sports.sina.com.cn/interface/rollnews_ch_out_interface.php?col=94&num=10000&date=%s"
    """
    url1 = "http://sports.sina.com.cn/t/2014-09-28/23537351504.shtml" #jinzhigui
    url2 = "http://sports.sina.com.cn/t/2014-11-01/02057391141.shtml" #feitianwang
    url3 = "http://sports.sina.com.cn/golf/2010-06-02/14325016287.shtml" #quanyunhui
    url4 = "http://sports.sina.com.cn/yayun2014/o/2014-09-28/23227351481.shtml"
    url5 = "http://sports.sina.com.cn/t/2014-09-28/21577351365.shtml"
    url6 = "http://sports.sina.com.cn/yayun2014/o/2014-09-28/17217350973.shtml"
    """
    url7 = "http://sports.sina.com.cn/golf/2012-11-06/15256286244.shtml"
    newsCrawler = NewsCrawler(url, "sina", "2012-1-1", "2013-1-2")
    newsCrawler.crawl_news(url7)
    return 

    con = pymongo.Connection('127.0.0.1')
    db = con['news']
    news = db.news_link.find().limit(500)

    start = None
    end = None
    count = 0
    for n in news:
        _LOGGER.info("News Count is %d" % count)
        url = n['url']
        start = time.time()
        newsCrawler.crawl_news(url)
        end = time.time()
        if end-start < 1:
            time.sleep(1 - end + start)
        count += 1
    
def main():
    crawl_list_test()

    #crawl_news_test()

if __name__ == "__main__":
    main()
