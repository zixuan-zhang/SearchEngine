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
from settings import _LOGGER, CMNT_BASE_URL, INTERVAL, NEWS_ID_REG,\
        NEWS_LIST_REG, XPATHS, NEWS_TYPE, BASE_ROLLPAGE_NODATE,\
        CRAWL_INTERVAL

class NewsCrawler():
    """
    Crawler Class
    """

    def __init__(self, basicUrl, site, startDate, endDate, interval=INTERVAL):
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
        while True:
            try:
                page = urllib2.urlopen(request).read()
                break
            except Exception, err:
                _LOGGER.warning("Open RollPage Error %s %s" % (rollpage, err))
                if count >= 3:
                    return []
                count += 1

        content_list = re.findall(NEWS_LIST_REG, page, re.M);
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
                    _LOGGER.warning("Extract News List Error %s %s" % (item, err))
                    break
                if key == "title":
                    value = value.decode('gbk')
                key = key.encode('utf-8')
                value = value.encode('utf-8')
                news[key] = value
            if(int(news['type']) in NEWS_TYPE):
                news_list.append(news)
                    
        return news_list

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
        reg = NEWS_LIST_REG
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

        titles = dom.xpath(XPATHS['title'])
        pubDate = dom.xpath(XPATHS['pubDate'])
        texts = dom.xpath(XPATHS['text'])
        comment = dom.xpath(XPATHS['commentId'])

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

    def news_crawler(self, MODE):
        """
        Class API
        """
        if MODE == 2:
            self.crawl_as_dates()
        elif MODE == 1:
            self.crawl_as_realtime()

    def crawl_as_realtime(self):
        while True:
            newsList = self.crawl_news_list(BASE_ROLLPAGE_NODATE)
            newsList = self.news_list_filter(newsList)
            _LOGGER.info("RealTime NewsList Count %d" % len(newsList))
            for news in newsList:
                self.crawl_news(news['url'])
                self.save_news_link(news)
            time.sleep(CRAWL_INTERVAL)

    def news_list_filter(self, newsList):
        newNewsList = []
        for news in newsList:
            if "url" not in news:
                _LOGGER.warning("NewsListParseError No Url")
            elif not newsdb.get_news_link({"url": news["url"]}):
                newNewsList.append(news)
        return newNewsList

    def crawl_as_dates(self):
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
            start = time.time()

            newsUrl = news["url"]
            result = self.crawl_news(newsUrl)
            if result:
                news['crawled'] = True
                self.save_news_link(news)
                _LOGGER.info("CRAWL_NEWS_SUC %s" % newsUrl)
            else:
                _LOGGER.warning("CRAWL_NEWS_FAILED %s" % newsUrl)

            cost = time.time() - start
            if cost < self.interval:
                time.sleep(self.interval - cost)
