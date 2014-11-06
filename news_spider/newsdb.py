#! /usr/bin/env python
#coding=utf-8

"""
Created on Sep 1, 2014

@Author: Zixuan Zhang

This Script Provides Basic DB Operation
"""

import pymongo

def _get_db(ip = "127.0.0.1"):
    con = pymongo.Connection(ip)
    db = con['sina_news']
    return db

db = _get_db()

def get_news_link(cond):
    return db.news_link.find_one(cond)

def insert_news_link(data):
    if 'url' not in data:
        raise Exception("Lack of Url Key")

    if not get_news_link({"url": data["url"]}):
        db.news_link.insert(data)

def get_news(cond):
    return db.news.find_one(cond)

def insert_news(data):
    if 'url' not in data:
        raise Exception("Lack of Url Key")
    if not get_news({"url": data['url']}):
        db.news.insert(data)
