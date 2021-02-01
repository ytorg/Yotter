from requests_futures.sessions import FuturesSession
from multiprocessing import Process
from werkzeug.datastructures import Headers
from concurrent.futures import as_completed
from numerize import numerize
from bs4 import BeautifulSoup
from operator import itemgetter, attrgetter
from re import findall
from nitter import user
import time, datetime
import requests
import bleach
import urllib
import json
import re

config = json.load(open('yotter-config.json'))

def get_feed(usernames, daysMaxOld=10, includeRT=True):
    '''
    Returns feed tweets given a set of usernames
    '''
    feedTweets = []
    with FuturesSession() as session:
        futures = [session.get(f'{config["nitterInstance"]}{u}') for u in usernames]
        for future in as_completed(futures):
            res = future.result().content.decode('utf-8')
            html = BeautifulSoup(res, "html.parser")
            feedPosts = user.get_feed_tweets(html)
            feedTweets.append(feedPosts)

    userFeed = []
    for feed in feedTweets:
        if not includeRT:
            for tweet in feed:
                if tweet['isRT']:
                    continue
                else:
                    userFeed.append(tweet)
        else:
            userFeed+=feed
    try:
        for uf in userFeed:
            if uf == 'emptyFeed':
                userFeed.remove(uf)
        userFeed.sort(key=lambda item:item['timeStamp'], reverse=True)
    except:
        print("Error sorting feed - nitter/feed.py")
        return userFeed
    return userFeed
