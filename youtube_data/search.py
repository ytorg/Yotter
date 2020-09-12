from youtube_data import proto, utils
from bs4 import BeautifulSoup as bs
from flask import Markup
import urllib.parse
import requests
import base64
import json

def page_number_to_sp_parameter(page, autocorrect, sort, filters):
    offset = (int(page) - 1)*20    # 20 results per page
    autocorrect = proto.nested(8, proto.uint(1, 1 - int(autocorrect) ))
    filters_enc = proto.nested(2, proto.uint(1, filters['time']) + proto.uint(2, filters['type']) + proto.uint(3, filters['duration']))
    result = proto.uint(1, sort) + filters_enc + autocorrect + proto.uint(9, offset) + proto.string(61, b'')
    return base64.urlsafe_b64encode(result).decode('ascii')

def search_by_terms(search_terms, page, autocorrect, sort, filters):
    url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(search_terms)
    headers = {
        'Host': 'www.youtube.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'X-YouTube-Client-Name': '1',
        'X-YouTube-Client-Version': '2.20180418',
    }
    url += "&pbj=1&sp=" + page_number_to_sp_parameter(page, autocorrect, sort, filters).replace("=", "%3D")
    content = requests.get(url, headers=headers).text

    info = json.loads(content)
    videos = get_videos_from_search(info)
    channels = get_channels_from_search(info)

    results = {
        "videos": videos,
        "channels": channels
    }
    return results

def get_channels_from_search(search):
    results = []
    search = search[1]['response']
    primaryContents = search['contents']['twoColumnSearchResultsRenderer']['primaryContents']
    items = primaryContents['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']

    for item in items:
        try:
            item['channelRenderer']
            channel = get_channel_renderer_item_info(item['channelRenderer'])
            results.append(channel)
        except KeyError:
            continue
    return results

def get_channel_renderer_item_info(item):
    try:
        suscribers = item['subscriberCountText']['simpleText'].split(" ")[0]
    except:
        suscribers = "?"
    
    try:
        description = utils.get_description_snippet_text(item['descriptionSnippet']['runs'])
    except KeyError:
        description = ""

    try:
        channel = {
            "channelId": item['channelId'],
            "username": item['title']['simpleText'],
            "thumbnail": "https:{}".format(item['thumbnail']['thumbnails'][0]['url'].replace("/", "~")),
            "description": Markup(str(description)),
            "suscribers": suscribers,
            "videos": item['videoCountText']['runs'][0]['text']
        }
    except KeyError:
        channel = {
            "channelId": item['channelId'],
            "username": item['title']['simpleText'],
            "avatar": item['thumbnail']['thumbnails'][0]['url'],
            "suscribers": suscribers
        }
    return channel

def get_videos_from_search(search):
    latest = []
    results = []
    search = search[1]['response']
    primaryContents = search['contents']['twoColumnSearchResultsRenderer']['primaryContents']
    items = primaryContents['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']

    for item in items:
        try:
            item['videoRenderer']
            video = get_video_renderer_item_info(item['videoRenderer'])
            results.append(video)
        except KeyError:
            continue

    # Sometimes Youtube will return an empty query. Try again.        
    return results

def get_video_renderer_item_info(item):
    published = ""
    views = ""
    isLive = False
    isUpcoming = False

    thumbnailOverlays = item['thumbnailOverlays']
    try:
        if 'UPCOMING' in str(thumbnailOverlays):
            start_time = item['upcomingEventData']['startTime']
            isUpcoming = True
            views = "-"
            published = "Scheduled"
    except KeyError:
        isUpcoming = False

    try:
        if 'LIVE' in str(thumbnailOverlays):
            isLive = True
            try:
                views = item['viewCountText']['simpleText']
            except:
                views = "Live"
            try:
                duration = item['lengthText']['simpleText']
            except:
                duration = "-"
            if published != "Scheduled":
                try:
                    published = item['publishedTimeText']['simpleText']
                except KeyError:
                    published = "None"
    except:
        isUpcoming = False
        isLive = False

    if not isUpcoming and not isLive:
        views = item['viewCountText']['simpleText']
        published = item['publishedTimeText']['simpleText']
        duration = item['lengthText']['simpleText']

    video = {
        'videoTitle':item['title']['runs'][0]['text'],
        'description':Markup(str(utils.get_description_snippet_text(item['descriptionSnippet']['runs']))),
        'views':views,
        'timeStamp':published,
        'duration':duration,
        'channelName':item['ownerText']['runs'][0]['text'],
        'authorUrl':"/channel/{}".format(item['ownerText']['runs'][0]['navigationEndpoint']['browseEndpoint']['browseId']),
        'channelId':item['ownerText']['runs'][0]['navigationEndpoint']['browseEndpoint']['browseId'],
        'id':item['videoId'],
        'videoUrl':"/watch?v={}".format(item['videoId']),
        'isLive':isLive,
        'isUpcoming':isUpcoming,
        'videoThumb':item['thumbnail']['thumbnails'][0]['url']
    }
    return video

