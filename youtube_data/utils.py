import requests
import urllib.parse
import json
from bs4 import BeautifulSoup as bs

nested_renderer_dispatch = {
    'singleColumnBrowseResultsRenderer',
    'twoColumnBrowseResultsRenderer', # Channel renderer
    'twoColumnSearchResultsRenderer',
}

# these renderers contain a list of renderers inside them
nested_renderer_list_dispatch = {
    'sectionListRenderer',
    'itemSectionRenderer',
    'gridRenderer',
    'playlistVideoListRenderer',
    'singleColumnWatchNextResults',
}

_item_types = {
    'movieRenderer',
    'didYouMeanRenderer',
    'showingResultsForRenderer',

    'videoRenderer',
    'compactVideoRenderer',
    'compactAutoplayRenderer',
    'videoWithContextRenderer',
    'gridVideoRenderer',
    'playlistVideoRenderer',

    'playlistRenderer',
    'compactPlaylistRenderer',
    'gridPlaylistRenderer',

    'radioRenderer',
    'compactRadioRenderer',
    'gridRadioRenderer',

    'showRenderer',
    'compactShowRenderer',
    'gridShowRenderer',


    'channelRenderer',
    'compactChannelRenderer',
    'gridChannelRenderer',
}


def getRenderers(data):
    renderers = []
    for renderer in nested_renderer_dispatch:
        renderers.append(data['contents'][renderer])
    return renderers

def getRenderedItems(renderer):
    '''Given a renderer, return its items'''
