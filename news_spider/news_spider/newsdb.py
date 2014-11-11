#! /usr/bin/env python
#coding=utf-8

"""
Created on Sep 1, 2014

@Author: Zixuan Zhang

This Script Provides Basic DB Operation
"""

import pymongo
from settings import DB_IP, DB_PORT

def _get_db():
    con = pymongo.Connection(DB_IP, DB_PORT)
    db = con['sina_news']
    return db

db = _get_db()

def get_news_link(cond):
    """
    Get News Link.
    Data Include: 
        title
        url
        time
        type.
    """
    return db.news_link.find_one(cond)

def insert_news_link(data):
    """
    Insert News Link.
    url unique.
    """
    if 'url' not in data:
        raise Exception("Lack of Url Key")

    if not get_news_link({"url": data["url"]}):
        db.news_link.insert(data)

def get_news(cond):
    """
    Get News Info
    Data Include: 
        url
        title
        pubDate
        text
        commentNumber
        titleLen
        textLen
    """
    return db.news.find_one(cond)

def insert_news(data):
    """
    Insert News.
    url unique
    """
    if 'url' not in data:
        raise Exception("Lack of Url Key")
    if not get_news({"url": data['url']}):
        db.news.insert(data)
