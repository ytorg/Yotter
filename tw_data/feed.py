from requests_futures.sessions import FuturesSession
from werkzeug.datastructures import Headers
from flask import Markup
from concurrent.futures import as_completed
from numerize import numerize
from bs4 import BeautifulSoup
from re import findall
import time, datetime
import requests
import bleach
import urllib
import json
import re

NITTERINSTANCE = "https://nitter.net/"

def get_feed(usernames, maxOld):
    '''
    Returns feed tweets given a set of usernames
    '''
    feedTweets = []
    with FuturesSession() as session:
        futures = [session.get('{instance}{user}'.format(instance=NITTERINSTANCE, user=u)) for u in usernames]
        for future in as_completed(futures):
            res = future.result().content.decode('utf-8')
            html = BeautifulSoup(res, "html.parser")
            userFeed = html.find_all('div', attrs={'class':'timeline-item'})
            if userFeed != []:
                    for post in userFeed[:-1]:
                        tweet = {}
                        date_time_str = post.find('span', attrs={'class':'tweet-date'}).find('a')['title'].replace(",","")
                        time = datetime.datetime.now() - datetime.datetime.strptime(date_time_str, '%d/%m/%Y %H:%M:%S')
                        if time.days >= maxOld:
                            continue

                        if post.find('div', attrs={'class':'pinned'}):
                            if post.find('div', attrs={'class':'pinned'}).find('span', attrs={'icon-pin'}):
                                continue
                        
                        tweet['originalPoster'] = post.find('a', attrs={'class':'username'}).text
                        tweet['twitterName'] = post.find('a', attrs={'class':'fullname'}).text
                        tweet['timeStamp'] = datetime.datetime.strptime(date_time_str, '%d/%m/%Y %H:%M:%S')
                        tweet['date'] = post.find('span', attrs={'class':'tweet-date'}).find('a').text
                        tweet['content'] = Markup(post.find('div',  attrs={'class':'tweet-content'}))
                        
                        if post.find('div', attrs={'class':'retweet-header'}):
                            tweet['username'] = post.find('div', attrs={'class':'retweet-header'}).find('div', attrs={'class':'icon-container'}).text
                            tweet['isRT'] = True
                        else:
                            tweet['username'] = tweet['originalPoster']
                            tweet['isRT'] = False
                        
                        tweet['profilePic'] = NITTERINSTANCE+post.find('a', attrs={'class':'tweet-avatar'}).find('img')['src'][1:]
                        url = NITTERINSTANCE + post.find('a', attrs={'class':'tweet-link'})['href'][1:]
                        if post.find('div', attrs={'class':'quote'}):
                            tweet['isReply'] = True
                            tweet['quote'] = post.find('div', attrs={'class':'quote'})
                            if tweet['quote'].find('div',  attrs={'class':'quote-text'}):
                                tweet['replyingTweetContent'] = Markup(tweet['quote'].find('div',  attrs={'class':'quote-text'}))
                                
                            if tweet['quote'].find('a', attrs={'class':'still-image'}):
                                tweet['replyAttachedImg'] = NITTERINSTANCE+tweet['quote'].find('a', attrs={'class':'still-image'})['href'][1:]
                            
                            if tweet['quote'].find('div', attrs={'class':'unavailable-quote'}):
                                tweet['replyingUser']="Unavailable"
                            else:
                                tweet['replyingUser']=tweet['quote'].find('a',  attrs={'class':'username'}).text
                            post.find('div', attrs={'class':'quote'}).decompose()

                        if post.find('div',  attrs={'class':'attachments'}):
                            if not post.find(class_='quote'):
                                if  post.find('div',  attrs={'class':'attachments'}).find('a', attrs={'class':'still-image'}):
                                    attachedImg = NITTERINSTANCE + post.find('div',  attrs={'class':'attachments'}).find('a')['href'][1:]
                        feedTweets.append(tweet)
    return feedTweets