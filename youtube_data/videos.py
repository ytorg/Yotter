from bs4 import BeautifulSoup as bs
from urllib.parse import unquote
from youtube_dl import YoutubeDL
import urllib.parse
import requests
import json

def get_renderer_key(renderer, key):
    for k in renderer:
        if key in k:
            return k[key]

def get_video_primary_info(datad, datai):
    contents = datai["contents"]["twoColumnWatchNextResults"]['results']['results']['contents']
    item = get_renderer_key(contents, "videoPrimaryInfoRenderer")
    details = datad['videoDetails']
    try:
        isUpcoming = details['isUpcoming']
        views = "Scheduled video"
    except:
        isUpcoming = False
    
    if not isUpcoming:
        views = details['viewCount']
    
    ydl = YoutubeDL()
    try:
        data = ydl.extract_info(details['videoId'], False)
        if not details['isLiveContent']:
            url = data['formats'][-1]['url']
        else:
            url = data['formats'][-1]['url']
    except:
        url = "#"
    try:
        primaryInfo = {
            "id": details['videoId'],
            "title": details['title'],
            "description": details['shortDescription'],
            "views": views,
            "duration": details['lengthSeconds'],
            "date": item['dateText']['simpleText'],
            "rating": details['averageRating'],
            "author": details['author'],
            "isPrivate": details['isPrivate'],
            "isLive": details['isLiveContent'],
            "isUpcoming": isUpcoming,
            "allowRatings": details['allowRatings'],
            "url":url,
            "thumbnail": details['thumbnail']['thumbnails'][0]['url']
        }
    except:
        # If error take only most common items
        primaryInfo = {
            "id": details['videoId'],
            "title": details['title'],
            "description": details['shortDescription'],
            "views": details['viewCount'],
            "duration": details['lengthSeconds'],
            "date": item['dateText']['simpleText'],
            "rating": details['averageRating'],
            "author": details['author'],
            "isPrivate":False,
            "isLive":details['isLiveContent'],
            "isUpcoming":isUpcoming,
            "allowRatings":True,
            "url":url,
            "thumbnail": details['thumbnail']['thumbnails'][0]['url']
        }
    return primaryInfo

def get_video_owner_info(data):
    contents = data["contents"]["twoColumnWatchNextResults"]['results']['results']['contents']
    item = get_renderer_key(contents, "videoSecondaryInfoRenderer")
    ownerItem = item['owner']['videoOwnerRenderer']

    ownerInfo = {
        "thumbnail": ownerItem['thumbnail']['thumbnails'][0]['url'],
        "username": ownerItem['title']['runs'][0]['text'],
        "id": ownerItem['title']['runs'][0]['navigationEndpoint']['browseEndpoint']['browseId'],
        "suscriberCount":ownerItem['subscriberCountText']['runs'][0]['text']
    }
    return ownerInfo

def get_video_info(id):
    headers = {"Accept-Language": "en-US,en;q=0.5"}
    encoded_search = urllib.parse.quote(id)
    BASE_URL = "https://youtube.com"

    url = f"{BASE_URL}/watch?v={encoded_search}"
    response = requests.get(url, headers=headers).text

    while 'window["ytInitialData"]' and 'window["ytInitialData"]' not in response:
        response = requests.get(url, headers=headers).text
    
    start = (
        response.index('window["ytInitialData"]')
        + len('window["ytInitialData"]')
        + 3
    )

    start2 = (
        response.index('window["ytInitialPlayerResponse"]')
        + len('window["ytInitialPlayerResponse"]') + 3
    )

    end1 = response.index("};", start) + 1
    end2 = response.index("};", start2) + 1
    jsonIni = response[start:end1]
    dataInitial = json.loads(jsonIni)

    jsonDet = response[start2:end2]
    dataDetails = json.loads(jsonDet)

    #title, views, date
    videoInfo = get_video_primary_info(dataDetails, dataInitial)
    ownerInfo = get_video_owner_info(dataInitial)

    '''soup = bs(response, "html.parser")
    soup = str(str(soup.find("div", attrs={"id":"player-wrap"}).find_all("script")).split("ytplayer.config =")[1]).split("url")
    for url in soup:
        if "googlevideo" in url:
            print(unquote(url.replace("\\", "")))'''
    info = {"video":videoInfo, "owner":ownerInfo}
    return info