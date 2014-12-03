#! /usr/bin/env python

import pymongo

def _connect():
    con = pymongo.Connection("127.0.0.1")
    db = con['sina_news']
    return db

db = _connect()

def loads_news():
    newsList = db.news.find({"textLen": {"$gt": 100}})
    print newsList.count()
    count = 1
    for news in newsList:
        fp = open(str(count), 'w')
        title = news['title'].encode('utf-8')
        pubDate = news['pubDate'].encode('utf-8')
        url = news['url']
        commentNumber = news['commentNumber']
        text = news['text'].encode('utf-8')
        fp.write("Title:%s\n" % title)
        fp.write("pubDate:%s\n" % pubDate)
        fp.write("url:%s\n" % url)
        fp.write("commentNumber:%d\n" % commentNumber)
        fp.write("text:%s" % text)
        fp.close()
        count += 1

def main():
    loads_news()

if __name__ == "__main__":
    main()

