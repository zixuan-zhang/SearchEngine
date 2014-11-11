"""
Created on Sep 5, 2014

@Athor: Zhang Zixuan

This Script Contains Service Settings
"""

import logging

# Service Mode
# Type : int
# 1 : Crawl News in Real Time
# 2 : Crawl News as Date
MODE = 1

# If Mode above set to be 2, START_DATE&END_DATE must be given
# Date format: YYYY-MM-DD
# Type : String
# START_DATE is Supposed Less Than END_DATE
START_DATE = "2013-10-10"
END_DATE = "2013-10-11"

# DB Settings
# TYPE : DB_IP   String
#        DP_PORT String
# Default to be "127.0.0.1" & 22
DB_IP = "127.0.0.1"
DB_PORT = 27017

# Log File Name
# Type : String
LOG_NAME = "log"
# Log Format
# Type : String
LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"

# Spider Settings

# Site
# Only Support Sina.com
# Type : String
SITE = "sina"
# Base RollPage Url, Date Parameter not Included
# Type : String
BASE_ROLLPAGE = "http://roll.sports.sina.com.cn/interface/rollnews_ch_out_interface.php?col=94&num=10000&date=%s"
# Base RollPage Url, No Date Parameter
BASE_ROLLPAGE_NODATE = "http://roll.sports.sina.com.cn/interface/rollnews_ch_out_interface.php?col=94&num=1000"
# Base Comment Get Url. NewsId Parameter Missed
# Type : String
CMNT_BASE_URL = "http://comment5.news.sina.com.cn/page/info?format=js&jsvar=pagedata&channel=ty&newsid=%s&group=0&page=1&list=all&fr=ct"
# NewsList Regular
NEWS_LIST_REG = r',title[^}]*'
# NewsId Regular
NEWS_ID_REG = """newsid:[0-9\-'"]+,"""
# NewsType Supported
# 1 for Regular Text News
# 2 for Image News
# 3 for Video News
# Defaul Text Only
NEWS_TYPE = [1]
# Xpath for News
XPATHS = {"title": "//div[@class='blkContainerSblk']/h1[@id='artibodyTitle']//text()",
     "pubDate": "//div[@class='blkContainerSblk']/div[@class='artInfo']/span[@id='pub_date']/text()",
     "text": "//div[@class='blkContainerSblk']/div[@id='artibody']/p/text()",
     "commentId": "//meta[@name='comment']/@content"}
# Crawl Interval
# Defaul 0
INTERVAL = 0
CRAWL_INTERVAL = 10*60 #10 Minutes

# Initialization
logging.basicConfig(filename = LOG_NAME, level = logging.INFO, format = LOG_FORMAT)
_LOGGER = logging.getLogger()
