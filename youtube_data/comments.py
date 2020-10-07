from youtube_data import proto
import json
import base64
import urllib
import requests
import re
import bleach
from flask import Markup

URL_ORIGIN = "/https://www.youtube.com"

def make_comment_ctoken(video_id, sort=0, offset=0, lc='', secret_key=''):
    video_id = proto.as_bytes(video_id)
    secret_key = proto.as_bytes(secret_key)
    

    page_info = proto.string(4,video_id) + proto.uint(6, sort)
    offset_information = proto.nested(4, page_info) + proto.uint(5, offset)
    if secret_key:
        offset_information = proto.string(1, secret_key) + offset_information

    page_params = proto.string(2, video_id)
    if lc:
        page_params += proto.string(6, proto.percent_b64encode(proto.string(15, lc)))

    result = proto.nested(2, page_params) + proto.uint(3,6) + proto.nested(6, offset_information)
    return base64.urlsafe_b64encode(result).decode('ascii')

def comment_replies_ctoken(video_id, comment_id, max_results=500):  

    params = proto.string(2, comment_id) + proto.uint(9, max_results)
    params = proto.nested(3, params)
    
    result = proto.nested(2, proto.string(2, video_id)) + proto.uint(3,6) + proto.nested(6, params)
    return base64.urlsafe_b64encode(result).decode('ascii')



mobile_headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'X-YouTube-Client-Name': '2',
    'X-YouTube-Client-Version': '2.20180823',
}
def request_comments(ctoken, replies=False):
    if replies: # let's make it use different urls for no reason despite all the data being encoded
        base_url = "https://m.youtube.com/watch_comment?action_get_comment_replies=1&ctoken="
    else:
        base_url = "https://m.youtube.com/watch_comment?action_get_comments=1&ctoken="
    url = base_url + ctoken.replace("=", "%3D") + "&pbj=1"

    for i in range(0,8):    # don't retry more than 8 times
        content = requests.get(url, headers=mobile_headers).text
        if content[0:4] == b")]}'":             # random closing characters included at beginning of response for some reason
            content = content[4:]
        elif content[0:10] == b'\n<!DOCTYPE':   # occasionally returns html instead of json for no reason
            content = b''
            print("got <!DOCTYPE>, retrying")
            continue
        break

    polymer_json = json.loads(content)
    return polymer_json


def single_comment_ctoken(video_id, comment_id):
    page_params = proto.string(2, video_id) + proto.string(6, proto.percent_b64encode(proto.string(15, comment_id)))

    result = proto.nested(2, page_params) + proto.uint(3,6)
    return base64.urlsafe_b64encode(result).decode('ascii')


def concat_texts(strings):
    '''Concatenates strings. Returns None if any of the arguments are None'''
    result = ''
    for string in strings:
        if string['text'] is None:
            return None
        result += string['text']
    return result

def parse_comment(raw_comment):
    cmnt = {}
    raw_comment = raw_comment['commentThreadRenderer']['comment']['commentRenderer']
    cmnt['author'] = raw_comment['authorText']['runs'][0]['text']
    cmnt['thumbnail'] = raw_comment['authorThumbnail']['thumbnails'][0]['url']
    cmnt['channel'] = raw_comment['authorEndpoint']['commandMetadata']['webCommandMetadata']['url']
    cmnt['text'] = Markup(bleach.linkify(concat_texts(raw_comment['contentText']['runs']).replace("\n", "<br>")))
    cmnt['date'] = raw_comment['publishedTimeText']['runs'][0]['text']
    
    try:
        cmnt['likes'] = raw_comment['likeCount']
    except:
        cmnt['likes'] = 0

    try:
        cmnt['replies'] = raw_comment['replyCount']
    except:
        cmnt['replies'] = 0

    cmnt['authorIsChannelOwner'] = raw_comment['authorIsChannelOwner']
    try:
        cmnt['pinned'] = raw_comment['pinnedCommentBadge']
        cmnt['pinned'] = True
    except:
        cmnt['pinned'] = False
    return cmnt

def post_process_comments_info(comments_info):
    comments = []
    for comment in comments_info[1]['response']['continuationContents']['commentSectionContinuation']['items']:        
        comments.append(parse_comment(comment))
    return comments
        


def video_comments(video_id, sort=0, offset=0, lc='', secret_key=''):
    comments_info = request_comments(make_comment_ctoken(video_id, sort, offset, lc, secret_key))
    comments_info = post_process_comments_info(comments_info)
    return comments_info
    return {}

