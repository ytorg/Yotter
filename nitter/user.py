from flask import Markup
from requests_futures.sessions import FuturesSession
from werkzeug.datastructures import Headers
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

##########################
#### Config variables ####
##########################
config = json.load(open('yotter-config.json'))
config['nitterInstance']

def get_user_info(username):
    response = urllib.request.urlopen(f'{config["nitterInstance"]}{username}').read()
    #rssFeed = feedparser.parse(response.content)

    html = BeautifulSoup(str(response), "lxml")
    if html.body.find('div', attrs={'class':'error-panel'}):
        return False
    else:
        html = html.body.find('div', attrs={'class':'profile-card'})

        if html.find('a', attrs={'class':'profile-card-fullname'}):
            fullName = html.find('a', attrs={'class':'profile-card-fullname'}).getText().encode('latin1').decode('unicode_escape').encode('latin1').decode('utf8')
        else:
            fullName = None

        if html.find('div', attrs={'class':'profile-bio'}):
            profileBio = html.find('div', attrs={'class':'profile-bio'}).getText().encode('latin1').decode('unicode_escape').encode('latin1').decode('utf8')
        else:
            profileBio = None

        user = {
            "profileFullName":fullName,
            "profileUsername":html.find('a', attrs={'class':'profile-card-username'}).string.encode('latin_1').decode('unicode_escape').encode('latin_1').decode('utf8'),
            "profileBio":profileBio,
            "tweets":html.find_all('span', attrs={'class':'profile-stat-num'})[0].string,
            "following":html.find_all('span', attrs={'class':'profile-stat-num'})[1].string,
            "followers":numerize.numerize(int(html.find_all('span', attrs={'class':'profile-stat-num'})[2].string.replace(",",""))),
            "likes":html.find_all('span', attrs={'class':'profile-stat-num'})[3].string,
            "profilePic":config['nitterInstance'] + html.find('a', attrs={'class':'profile-card-avatar'})['href'][1:],
        }
        return user

def get_tweets(user, page=1):
    feed = urllib.request.urlopen(f'{config["nitterInstance"]}{user}').read()
    #Gather feedPosts
    res = feed.decode('utf-8')
    html = BeautifulSoup(res, "html.parser")
    feedPosts = get_feed_tweets(html)

    if page == 2:
        nextPage = html.find('div', attrs={'class':'show-more'}).find('a')['href']
        url = f'{config["nitterInstance"]}{user}{nextPage}'
        print(url)
        feed = urllib.request.urlopen(url).read()
        res = feed.decode('utf-8')
        html = BeautifulSoup(res, "html.parser")
        feedPosts = get_feed_tweets(html)
    return feedPosts

def yotterify(text):
    URLS = ['https://youtube.com']
    text = str(text)
    for url in URLS:
        text.replace(url, "")
    return text

def get_feed_tweets(html):
    feedPosts = []
    if 'No items found' in str(html.body):
        return 'Empty feed'
    if "This account's tweets are protected." in str(html.body):
        return 'Protected feed'
    userFeed = html.find_all('div', attrs={'class':'timeline-item'})
    if userFeed != []:
        for post in userFeed[:-1]:
            if 'show-more' in str(post):
                continue
            date_time_str = post.find('span', attrs={'class':'tweet-date'}).find('a')['title'].replace(",","")

            if post.find('div', attrs={'class':'pinned'}):
                if post.find('div', attrs={'class':'pinned'}).find('span', attrs={'icon-pin'}):
                    continue

            tweet = {}
            tweet['op'] = post.find('a', attrs={'class':'username'}).text
            tweet['twitterName'] = post.find('a', attrs={'class':'fullname'}).text
            tweet['timeStamp'] = str(datetime.datetime.strptime(date_time_str, '%d/%m/%Y %H:%M:%S'))
            tweet['date'] = post.find('span', attrs={'class':'tweet-date'}).find('a').text
            tweet['content'] = Markup(yotterify(post.find('div',  attrs={'class':'tweet-content'}).decode_contents().replace("\n", "<br>")))

            if post.find('div', attrs={'class':'retweet-header'}):
                tweet['username'] = post.find('div', attrs={'class':'retweet-header'}).find('div', attrs={'class':'icon-container'}).text
                tweet['isRT'] = True
            else:
                tweet['username'] = tweet['op']
                tweet['isRT'] = False

            tweet['profilePic'] = config['nitterInstance']+post.find('a', attrs={'class':'tweet-avatar'}).find('img')['src'][1:]
            tweet['url'] = config['nitterInstance'] + post.find('a', attrs={'class':'tweet-link'})['href'][1:]

            # Is quoting another tweet
            if post.find('div', attrs={'class':'quote'}):
                tweet['isReply'] = True
                quote = post.find('div', attrs={'class':'quote'})

                if 'unavailable' in str(quote):
                    tweet['unavailableReply'] = True
                else:
                    tweet['unavailableReply'] = False

                if not tweet['unavailableReply']:
                    if quote.find('div',  attrs={'class':'quote-text'}):
                        try:
                            tweet['replyingTweetContent'] = Markup(quote.find('div',  attrs={'class':'quote-text'}).replace("\n", "<br>"))
                        except:
                            tweet['replyingTweetContent'] = Markup(quote.find('div',  attrs={'class':'quote-text'}))

                    if quote.find('a', attrs={'class':'still-image'}):
                        tweet['replyAttachedImages'] = []
                        images = quote.find_all('a',  attrs={'class':'still-image'})
                        for img in images:
                            img = BeautifulSoup(str(img), "lxml")
                            url = config['nitterInstance'] + img.find('a')['href'][1:]
                            tweet['replyAttachedImages'].append(url)
                    tweet['replyingUser']=quote.find('a',  attrs={'class':'username'}).text
                    post.find('div', attrs={'class':'quote'}).decompose()
            else:
                tweet['isReply'] = False

            # Has attatchments
            if post.find('div',  attrs={'class':'attachments'}):
                # Images
                if  post.find('div',  attrs={'class':'attachments'}).find('a', attrs={'class':'still-image'}):
                    tweet['attachedImages'] = []
                    images = post.find('div',  attrs={'class':'attachments'}).find_all('a', attrs={'class':'still-image'})
                    for img in images:
                        img = BeautifulSoup(str(img), 'lxml')
                        url = config['nitterInstance'] + img.find('a')['href'][1:]
                        tweet['attachedImages'].append(url)
                else:
                    tweet['attachedImages'] = False
                # Videos    
                if post.find('div', attrs={'attachments'}).find('div', attrs={'gallery-video'}):
                    tweet['attachedVideo'] = True
                else:
                    tweet['attachedVideo'] = False
            else:
                tweet['attachedVideo'] = False
                tweet['attachedImages'] = False

            if post.find('div', attrs={'class':'tweet-stats'}):
                stats = post.find('div', attrs={'class':'tweet-stats'}).find_all('span', attrs={'class':'tweet-stat'})
                for stat in stats:
                    if 'comment' in str(stat):
                        tweet['comments'] = stat.find('div',attrs={'class':'icon-container'}).text
                    elif 'retweet' in str(stat):
                        tweet['retweets'] = stat.find('div',attrs={'class':'icon-container'}).text
                    elif 'heart' in str(stat):
                        tweet['likes'] = stat.find('div',attrs={'class':'icon-container'}).text
                    else:
                        tweet['quotes'] =  stat.find('div',attrs={'class':'icon-container'}).text
            feedPosts.append(tweet)
    else:
        return {"emptyFeed": True}
    return feedPosts
