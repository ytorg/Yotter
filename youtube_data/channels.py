from youtube_data import proto, utils
from flask import Markup as mk
import requests
import base64
import json
import re

# From: https://github.com/user234683/youtube-local/blob/master/youtube/channel.py
# SORT:
# videos:
#    Popular - 1
#    Oldest - 2
#    Newest - 3
# playlists:
#    Oldest - 2
#    Newest - 3
#    Last video added - 4

# view:
# grid: 0 or 1
# list: 2

headers = {
        'Host': 'www.youtube.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'X-YouTube-Client-Name': '1',
        'X-YouTube-Client-Version': '2.20180418',
    }
real_cookie = (('Cookie', 'VISITOR_INFO1_LIVE=8XihrAcN1l4'),)
generic_cookie = (('Cookie', 'VISITOR_INFO1_LIVE=ST1Ti53r4fU'),)


def channel_ctoken_desktop(channel_id, page, sort, tab, view=1):
    # see https://github.com/iv-org/invidious/issues/1319#issuecomment-671732646
    # page > 1 doesn't work when sorting by oldest
    offset = 30*(int(page) - 1)
    schema_number = {
        3: 6307666885028338688,
        2: 17254859483345278706,
        1: 16570086088270825023,
    }[int(sort)]
    page_token = proto.string(61, proto.unpadded_b64encode(proto.string(1,
            proto.uint(1, schema_number) + proto.string(2,
                proto.string(1, proto.unpadded_b64encode(proto.uint(1,offset)))
            )
    )))

    tab = proto.string(2, tab )
    sort = proto.uint(3, int(sort))
    #page = proto.string(15, str(page) )

    shelf_view = proto.uint(4, 0)
    view = proto.uint(6, int(view))
    continuation_info = proto.string(3,
        proto.percent_b64encode(tab + sort + shelf_view + view + page_token)
    )

    channel_id = proto.string(2, channel_id )
    pointless_nest = proto.string(80226972, channel_id + continuation_info)

    return base64.urlsafe_b64encode(pointless_nest).decode('ascii')

def channel_ctoken_mobile(channel_id, page, sort, tab, view=1):
    tab = proto.string(2, tab )
    sort = proto.uint(3, int(sort))
    page = proto.string(15, str(page) )
    # example with shelves in videos tab: https://www.youtube.com/channel/UCNL1ZadSjHpjm4q9j2sVtOA/videos
    shelf_view = proto.uint(4, 0)
    view = proto.uint(6, int(view))
    continuation_info = proto.string( 3, proto.percent_b64encode(tab + view + sort + shelf_view + page) )

    channel_id = proto.string(2, channel_id )
    pointless_nest = proto.string(80226972, channel_id + continuation_info)

    return base64.urlsafe_b64encode(pointless_nest).decode('ascii')


def id_or_username(string):
    cidRegex = "^UC.{22}$"
    if re.match(cidRegex, string):
        return "channel"
    else:
        return "user"

def get_channel_videos_tab(content):
    tabs = content['contents']['twoColumnBrowseResultsRenderer']['tabs']
    for tab in tabs:
        if tab['title'] != "Videos":
            continue
        else:
            return tab

def get_video_items_from_tab(tab):
    items = []
    for item in tab:
        try:
            if item['gridVideoRenderer']:
                items.append(item)
            else:
                continue
        except KeyError:
            continue
    return items

def get_info_grid_video_item(item, channel=None):
    item = item['gridVideoRenderer']
    thumbnailOverlays = item['thumbnailOverlays']
    published = ""
    views = ""
    isLive = False
    isUpcoming = False
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
    except KeyError:
        isUpcoming = False
        isLive = False

    if not isUpcoming and not isLive:
        views = item['viewCountText']['simpleText']
        published = item['publishedTimeText']['simpleText']
        try:
            duration = item['lengthText']['simpleText']
        except:
            duration = "?"

    video = {
        'videoTitle':item['title']['runs'][0]['text'],
        'description':"",
        'views':views,
        'timeStamp':published,
        'duration':duration,
        'channelName':channel['username'],
        'authorUrl':"/channel/{}".format(channel['channelId']),
        'channelId':channel['channelId'],
        'id':item['videoId'],
        'videoUrl':"/watch?v={}".format(item['videoId']),
        'isLive':isLive,
        'isUpcoming':isUpcoming,
        'videoThumb':item['thumbnail']['thumbnails'][0]['url']
    }
    return video

def get_author_info_from_channel(content):
    hmd = content['metadata']['channelMetadataRenderer']
    cmd = content['header']['c4TabbedHeaderRenderer']
    description = mk(hmd['description'])
    channel = {
        "channelId": cmd['channelId'],
        "username": cmd['title'],
        "thumbnail": "https:{}".format(cmd['avatar']['thumbnails'][0]['url'].replace("/", "~")),
        "description":description,
        "suscribers": cmd['subscriberCountText']['runs'][0]['text'].split(" ")[0],
        "banner": cmd['banner']['thumbnails'][0]['url']
    }
    return channel

def get_channel_info(channelId, videos=True, page=1, sort=3):
    if id_or_username(channelId) == "channel":
        videos = []
        ciUrl = "https://www.youtube.com/channel/{}".format(channelId)
        mainUrl = "https://www.youtube.com/browse_ajax?ctoken={}".format(channel_ctoken_desktop(channelId, page, sort, "videos"))
        content = json.loads(requests.get(mainUrl, headers=headers).text)
        req = requests.get(ciUrl, headers=headers).text

        start = (
            req.index('window["ytInitialData"]')
            + len('window["ytInitialData"]')
            + 3
        )

        end = req.index("};", start) + 1
        jsonIni = req[start:end]
        data = json.loads(jsonIni)

        #videosTab = get_channel_videos_tab(content)
        authorInfo = get_author_info_from_channel(data)
        if videos:
            gridVideoItemList = get_video_items_from_tab(content[1]['response']['continuationContents']['gridContinuation']['items'])
            for video in gridVideoItemList:
                vid = get_info_grid_video_item(video, authorInfo)
                videos.append(vid)
            print({"channel":authorInfo, "videos":videos})
            return {"channel":authorInfo, "videos":videos}
        else:
            return {"channel":authorInfo}

    else:
        baseUrl = "https://www.youtube.com/user/{}".format(channelId)