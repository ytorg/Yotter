import urllib
from flask import Markup
import bleach
def get_description_snippet_text(ds):
    string = ""
    for t in ds:
        try:
            if t['bold']:
                text = "<b>"+t['text']+"</b>"
            else:
                text = t['text']
        except:
            text = t['text']
        string = string + text
    return string


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
    cmnt['author'] = raw_comment['author']
    cmnt['thumbnail'] = raw_comment['author_avatar']

    cmnt['channel'] = raw_comment['author_url']
    cmnt['text'] = Markup(bleach.linkify(concat_texts(raw_comment['text']).replace("\n", "<br>")))
    cmnt['date'] = raw_comment['time_published']

    try:
        cmnt['creatorHeart'] = raw_comment['creatorHeart']['creatorHeartRenderer']['creatorThumbnail']['thumbnails'][0][
            'url']
    except:
        cmnt['creatorHeart'] = False

    try:
        cmnt['likes'] = raw_comment['like_count']
    except:
        cmnt['likes'] = 0

    try:
        cmnt['replies'] = raw_comment['reply_count']
    except:
        cmnt['replies'] = 0
    return cmnt


def post_process_comments_info(comments_info):
    comments = []
    for comment in comments_info['comments']:
        comments.append(parse_comment(comment))
    return comments