from bs4 import BeautifulSoup as bs
from urllib.parse import unquote
from youtube_dl import YoutubeDL
import urllib.parse
import requests
import json

# from https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/extractor/youtube.py
_formats = {
    '5': {'ext': 'flv', 'width': 400, 'height': 240, 'acodec': 'mp3', 'audio_bitrate': 64, 'vcodec': 'h263'},
    '6': {'ext': 'flv', 'width': 450, 'height': 270, 'acodec': 'mp3', 'audio_bitrate': 64, 'vcodec': 'h263'},
    '13': {'ext': '3gp', 'acodec': 'aac', 'vcodec': 'mp4v'},
    '17': {'ext': '3gp', 'width': 176, 'height': 144, 'acodec': 'aac', 'audio_bitrate': 24, 'vcodec': 'mp4v'},
    '18': {'ext': 'mp4', 'width': 640, 'height': 360, 'acodec': 'aac', 'audio_bitrate': 96, 'vcodec': 'h264'},
    '22': {'ext': 'mp4', 'width': 1280, 'height': 720, 'acodec': 'aac', 'audio_bitrate': 192, 'vcodec': 'h264'},
    '34': {'ext': 'flv', 'width': 640, 'height': 360, 'acodec': 'aac', 'audio_bitrate': 128, 'vcodec': 'h264'},
    '35': {'ext': 'flv', 'width': 854, 'height': 480, 'acodec': 'aac', 'audio_bitrate': 128, 'vcodec': 'h264'},
    # itag 36 videos are either 320x180 (BaW_jenozKc) or 320x240 (__2ABJjxzNo), audio_bitrate varies as well
    '36': {'ext': '3gp', 'width': 320, 'acodec': 'aac', 'vcodec': 'mp4v'},
    '37': {'ext': 'mp4', 'width': 1920, 'height': 1080, 'acodec': 'aac', 'audio_bitrate': 192, 'vcodec': 'h264'},
    '38': {'ext': 'mp4', 'width': 4096, 'height': 3072, 'acodec': 'aac', 'audio_bitrate': 192, 'vcodec': 'h264'},
    '43': {'ext': 'webm', 'width': 640, 'height': 360, 'acodec': 'vorbis', 'audio_bitrate': 128, 'vcodec': 'vp8'},
    '44': {'ext': 'webm', 'width': 854, 'height': 480, 'acodec': 'vorbis', 'audio_bitrate': 128, 'vcodec': 'vp8'},
    '45': {'ext': 'webm', 'width': 1280, 'height': 720, 'acodec': 'vorbis', 'audio_bitrate': 192, 'vcodec': 'vp8'},
    '46': {'ext': 'webm', 'width': 1920, 'height': 1080, 'acodec': 'vorbis', 'audio_bitrate': 192, 'vcodec': 'vp8'},
    '59': {'ext': 'mp4', 'width': 854, 'height': 480, 'acodec': 'aac', 'audio_bitrate': 128, 'vcodec': 'h264'},
    '78': {'ext': 'mp4', 'width': 854, 'height': 480, 'acodec': 'aac', 'audio_bitrate': 128, 'vcodec': 'h264'},


    # 3D videos
    '82': {'ext': 'mp4', 'height': 360, 'format_note': '3D', 'acodec': 'aac', 'audio_bitrate': 128, 'vcodec': 'h264'},
    '83': {'ext': 'mp4', 'height': 480, 'format_note': '3D', 'acodec': 'aac', 'audio_bitrate': 128, 'vcodec': 'h264'},
    '84': {'ext': 'mp4', 'height': 720, 'format_note': '3D', 'acodec': 'aac', 'audio_bitrate': 192, 'vcodec': 'h264'},
    '85': {'ext': 'mp4', 'height': 1080, 'format_note': '3D', 'acodec': 'aac', 'audio_bitrate': 192, 'vcodec': 'h264'},
    '100': {'ext': 'webm', 'height': 360, 'format_note': '3D', 'acodec': 'vorbis', 'audio_bitrate': 128, 'vcodec': 'vp8'},
    '101': {'ext': 'webm', 'height': 480, 'format_note': '3D', 'acodec': 'vorbis', 'audio_bitrate': 192, 'vcodec': 'vp8'},
    '102': {'ext': 'webm', 'height': 720, 'format_note': '3D', 'acodec': 'vorbis', 'audio_bitrate': 192, 'vcodec': 'vp8'},

    # Apple HTTP Live Streaming
    '91': {'ext': 'mp4', 'height': 144, 'format_note': 'HLS', 'acodec': 'aac', 'audio_bitrate': 48, 'vcodec': 'h264'},
    '92': {'ext': 'mp4', 'height': 240, 'format_note': 'HLS', 'acodec': 'aac', 'audio_bitrate': 48, 'vcodec': 'h264'},
    '93': {'ext': 'mp4', 'height': 360, 'format_note': 'HLS', 'acodec': 'aac', 'audio_bitrate': 128, 'vcodec': 'h264'},
    '94': {'ext': 'mp4', 'height': 480, 'format_note': 'HLS', 'acodec': 'aac', 'audio_bitrate': 128, 'vcodec': 'h264'},
    '95': {'ext': 'mp4', 'height': 720, 'format_note': 'HLS', 'acodec': 'aac', 'audio_bitrate': 256, 'vcodec': 'h264'},
    '96': {'ext': 'mp4', 'height': 1080, 'format_note': 'HLS', 'acodec': 'aac', 'audio_bitrate': 256, 'vcodec': 'h264'},
    '132': {'ext': 'mp4', 'height': 240, 'format_note': 'HLS', 'acodec': 'aac', 'audio_bitrate': 48, 'vcodec': 'h264'},
    '151': {'ext': 'mp4', 'height': 72, 'format_note': 'HLS', 'acodec': 'aac', 'audio_bitrate': 24, 'vcodec': 'h264'},

    # DASH mp4 video
    '133': {'ext': 'mp4', 'height': 240, 'format_note': 'DASH video', 'vcodec': 'h264'},
    '134': {'ext': 'mp4', 'height': 360, 'format_note': 'DASH video', 'vcodec': 'h264'},
    '135': {'ext': 'mp4', 'height': 480, 'format_note': 'DASH video', 'vcodec': 'h264'},
    '136': {'ext': 'mp4', 'height': 720, 'format_note': 'DASH video', 'vcodec': 'h264'},
    '137': {'ext': 'mp4', 'height': 1080, 'format_note': 'DASH video', 'vcodec': 'h264'},
    '138': {'ext': 'mp4', 'format_note': 'DASH video', 'vcodec': 'h264'},  # Height can vary (https://github.com/ytdl-org/youtube-dl/issues/4559)
    '160': {'ext': 'mp4', 'height': 144, 'format_note': 'DASH video', 'vcodec': 'h264'},
    '212': {'ext': 'mp4', 'height': 480, 'format_note': 'DASH video', 'vcodec': 'h264'},
    '264': {'ext': 'mp4', 'height': 1440, 'format_note': 'DASH video', 'vcodec': 'h264'},
    '298': {'ext': 'mp4', 'height': 720, 'format_note': 'DASH video', 'vcodec': 'h264', 'fps': 60},
    '299': {'ext': 'mp4', 'height': 1080, 'format_note': 'DASH video', 'vcodec': 'h264', 'fps': 60},
    '266': {'ext': 'mp4', 'height': 2160, 'format_note': 'DASH video', 'vcodec': 'h264'},

    # Dash mp4 audio
    '139': {'ext': 'm4a', 'format_note': 'DASH audio', 'acodec': 'aac', 'audio_bitrate': 48, 'container': 'm4a_dash'},
    '140': {'ext': 'm4a', 'format_note': 'DASH audio', 'acodec': 'aac', 'audio_bitrate': 128, 'container': 'm4a_dash'},
    '141': {'ext': 'm4a', 'format_note': 'DASH audio', 'acodec': 'aac', 'audio_bitrate': 256, 'container': 'm4a_dash'},
    '256': {'ext': 'm4a', 'format_note': 'DASH audio', 'acodec': 'aac', 'container': 'm4a_dash'},
    '258': {'ext': 'm4a', 'format_note': 'DASH audio', 'acodec': 'aac', 'container': 'm4a_dash'},
    '325': {'ext': 'm4a', 'format_note': 'DASH audio', 'acodec': 'dtse', 'container': 'm4a_dash'},
    '328': {'ext': 'm4a', 'format_note': 'DASH audio', 'acodec': 'ec-3', 'container': 'm4a_dash'},

    # Dash webm
    '167': {'ext': 'webm', 'height': 360, 'width': 640, 'format_note': 'DASH video', 'container': 'webm', 'vcodec': 'vp8'},
    '168': {'ext': 'webm', 'height': 480, 'width': 854, 'format_note': 'DASH video', 'container': 'webm', 'vcodec': 'vp8'},
    '169': {'ext': 'webm', 'height': 720, 'width': 1280, 'format_note': 'DASH video', 'container': 'webm', 'vcodec': 'vp8'},
    '170': {'ext': 'webm', 'height': 1080, 'width': 1920, 'format_note': 'DASH video', 'container': 'webm', 'vcodec': 'vp8'},
    '218': {'ext': 'webm', 'height': 480, 'width': 854, 'format_note': 'DASH video', 'container': 'webm', 'vcodec': 'vp8'},
    '219': {'ext': 'webm', 'height': 480, 'width': 854, 'format_note': 'DASH video', 'container': 'webm', 'vcodec': 'vp8'},
    '278': {'ext': 'webm', 'height': 144, 'format_note': 'DASH video', 'container': 'webm', 'vcodec': 'vp9'},
    '242': {'ext': 'webm', 'height': 240, 'format_note': 'DASH video', 'vcodec': 'vp9'},
    '243': {'ext': 'webm', 'height': 360, 'format_note': 'DASH video', 'vcodec': 'vp9'},
    '244': {'ext': 'webm', 'height': 480, 'format_note': 'DASH video', 'vcodec': 'vp9'},
    '245': {'ext': 'webm', 'height': 480, 'format_note': 'DASH video', 'vcodec': 'vp9'},
    '246': {'ext': 'webm', 'height': 480, 'format_note': 'DASH video', 'vcodec': 'vp9'},
    '247': {'ext': 'webm', 'height': 720, 'format_note': 'DASH video', 'vcodec': 'vp9'},
    '248': {'ext': 'webm', 'height': 1080, 'format_note': 'DASH video', 'vcodec': 'vp9'},
    '271': {'ext': 'webm', 'height': 1440, 'format_note': 'DASH video', 'vcodec': 'vp9'},
    # itag 272 videos are either 3840x2160 (e.g. RtoitU2A-3E) or 7680x4320 (sLprVF6d7Ug)
    '272': {'ext': 'webm', 'height': 2160, 'format_note': 'DASH video', 'vcodec': 'vp9'},
    '302': {'ext': 'webm', 'height': 720, 'format_note': 'DASH video', 'vcodec': 'vp9', 'fps': 60},
    '303': {'ext': 'webm', 'height': 1080, 'format_note': 'DASH video', 'vcodec': 'vp9', 'fps': 60},
    '308': {'ext': 'webm', 'height': 1440, 'format_note': 'DASH video', 'vcodec': 'vp9', 'fps': 60},
    '313': {'ext': 'webm', 'height': 2160, 'format_note': 'DASH video', 'vcodec': 'vp9'},
    '315': {'ext': 'webm', 'height': 2160, 'format_note': 'DASH video', 'vcodec': 'vp9', 'fps': 60},

    # Dash webm audio
    '171': {'ext': 'webm', 'acodec': 'vorbis', 'format_note': 'DASH audio', 'audio_bitrate': 128},
    '172': {'ext': 'webm', 'acodec': 'vorbis', 'format_note': 'DASH audio', 'audio_bitrate': 256},

    # Dash webm audio with opus inside
    '249': {'ext': 'webm', 'format_note': 'DASH audio', 'acodec': 'opus', 'audio_bitrate': 50},
    '250': {'ext': 'webm', 'format_note': 'DASH audio', 'acodec': 'opus', 'audio_bitrate': 70},
    '251': {'ext': 'webm', 'format_note': 'DASH audio', 'acodec': 'opus', 'audio_bitrate': 160},

    # RTMP (unnamed)
    '_rtmp': {'protocol': 'rtmp'},

    # av01 video only formats sometimes served with "unknown" codecs
    '394': {'vcodec': 'av01.0.05M.08'},
    '395': {'vcodec': 'av01.0.05M.08'},
    '396': {'vcodec': 'av01.0.05M.08'},
    '397': {'vcodec': 'av01.0.05M.08'},
}


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

        ## Get audio
        audio_urls = []
        for f in data['formats']:
            for fid in _formats:
                if f['format_id'] == fid:
                    try:
                        if 'audio' in _formats[fid]['format_note']:
                            aurl = f['url']
                            fnote = _formats[fid]['format_note']
                            bitrate = _formats[fid]['audio_bitrate']
                            audio_inf = {
                                "url":aurl,
                                "id":fnote,
                                "btr": bitrate
                            }
                            audio_urls.append(audio_inf)
                    except:
                        continue
        ## Get video
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
            "thumbnail": details['thumbnail']['thumbnails'][0]['url'],
            "audio": audio_urls[-1]
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
            "thumbnail": details['thumbnail']['thumbnails'][0]['url'],
            "audio": audio_urls[-1]
        }
    return primaryInfo

def get_video_owner_info(data):
    contents = data["contents"]["twoColumnWatchNextResults"]['results']['results']['contents']
    item = get_renderer_key(contents, "videoSecondaryInfoRenderer")
    ownerItem = item['owner']['videoOwnerRenderer']

    try:
        sC = ownerItem['subscriberCountText']['runs'][0]['text']
    except:
        sC = "Unknown"
    ownerInfo = {
        "thumbnail": ownerItem['thumbnail']['thumbnails'][0]['url'],
        "username": ownerItem['title']['runs'][0]['text'],
        "id": ownerItem['title']['runs'][0]['navigationEndpoint']['browseEndpoint']['browseId'],
        "suscriberCount":sC
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