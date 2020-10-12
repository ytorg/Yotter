import json
import math
import traceback
import urllib

from youtube import util, yt_data_extract


def get_video_sources(info, tor_bypass=False):
    video_sources = []
    max_resolution = 1080
    for fmt in info['formats']:
        if not all(fmt[attr] for attr in ('quality', 'width', 'ext', 'url')):
            continue
        if fmt['acodec'] and fmt['vcodec'] and (fmt['height'] <= max_resolution):
            video_sources.append({
                'src': fmt['url'],
                'type': 'video/' + fmt['ext'],
                'quality': fmt['quality'],
                'height': fmt['height'],
                'width': fmt['width'],
            })

    #### order the videos sources so the preferred resolution is first ###

    video_sources.sort(key=lambda source: source['quality'], reverse=True)

    return video_sources

def make_caption_src(info, lang, auto=False, trans_lang=None):
    label = lang
    if auto:
        label += ' (Automatic)'
    if trans_lang:
        label += ' -> ' + trans_lang
    return {
        'url': '/' + yt_data_extract.get_caption_url(info, lang, 'vtt', auto, trans_lang),
        'label': label,
        'srclang': trans_lang[0:2] if trans_lang else lang[0:2],
        'on': False,
    }

def lang_in(lang, sequence):
    '''Tests if the language is in sequence, with e.g. en and en-US considered the same'''
    if lang is None:
        return False
    lang = lang[0:2]
    return lang in (l[0:2] for l in sequence)

def lang_eq(lang1, lang2):
    '''Tests if two iso 639-1 codes are equal, with en and en-US considered the same.
       Just because the codes are equal does not mean the dialects are mutually intelligible, but this will have to do for now without a complex language model'''
    if lang1 is None or lang2 is None:
        return False
    return lang1[0:2] == lang2[0:2]

def equiv_lang_in(lang, sequence):
    '''Extracts a language in sequence which is equivalent to lang.
    e.g. if lang is en, extracts en-GB from sequence.
    Necessary because if only a specific variant like en-GB is available, can't ask Youtube for simply en. Need to get the available variant.'''
    lang = lang[0:2]
    for l in sequence:
        if l[0:2] == lang:
            return l
    return None

def get_subtitle_sources(info):
    '''Returns these sources, ordered from least to most intelligible:
    native_video_lang (Automatic)
    foreign_langs (Manual)
    native_video_lang (Automatic) -> pref_lang
    foreign_langs (Manual) -> pref_lang
    native_video_lang (Manual) -> pref_lang
    pref_lang (Automatic)
    pref_lang (Manual)'''
    sources = []
    pref_lang = 'en'
    native_video_lang = None
    if info['automatic_caption_languages']:
        native_video_lang = info['automatic_caption_languages'][0]

    highest_fidelity_is_manual = False

    # Sources are added in very specific order outlined above
    # More intelligible sources are put further down to avoid browser bug when there are too many languages
    # (in firefox, it is impossible to select a language near the top of the list because it is cut off)

    # native_video_lang (Automatic)
    if native_video_lang and not lang_eq(native_video_lang, pref_lang):
        sources.append(make_caption_src(info, native_video_lang, auto=True))

    # foreign_langs (Manual)
    for lang in info['manual_caption_languages']:
        if not lang_eq(lang, pref_lang):
            sources.append(make_caption_src(info, lang))

    if (lang_in(pref_lang, info['translation_languages'])
            and not lang_in(pref_lang, info['automatic_caption_languages'])
            and not lang_in(pref_lang, info['manual_caption_languages'])):
        # native_video_lang (Automatic) -> pref_lang
        if native_video_lang and not lang_eq(pref_lang, native_video_lang):
            sources.append(make_caption_src(info, native_video_lang, auto=True, trans_lang=pref_lang))

        # foreign_langs (Manual) -> pref_lang
        for lang in info['manual_caption_languages']:
            if not lang_eq(lang, native_video_lang) and not lang_eq(lang, pref_lang):
                sources.append(make_caption_src(info, lang, trans_lang=pref_lang))

        # native_video_lang (Manual) -> pref_lang
        if lang_in(native_video_lang, info['manual_caption_languages']):
            sources.append(make_caption_src(info, native_video_lang, trans_lang=pref_lang))

    # pref_lang (Automatic)
    if lang_in(pref_lang, info['automatic_caption_languages']):
        sources.append(make_caption_src(info, equiv_lang_in(pref_lang, info['automatic_caption_languages']), auto=True))

    # pref_lang (Manual)
    if lang_in(pref_lang, info['manual_caption_languages']):
        sources.append(make_caption_src(info, equiv_lang_in(pref_lang, info['manual_caption_languages'])))
        highest_fidelity_is_manual = True
    if len(sources) == 0:
        assert len(info['automatic_caption_languages']) == 0 and len(info['manual_caption_languages']) == 0

    return sources

def decrypt_signatures(info):
    '''return error string, or False if no errors'''
    if not yt_data_extract.requires_decryption(info):
        return False
    if not info['player_name']:
        return 'Could not find player name'
    if not info['base_js']:
        return 'Failed to find base.js'

    player_name = info['player_name']
    base_js = util.fetch_url(info['base_js'], debug_name='base.js', report_text='Fetched player ' + player_name)
    base_js = base_js.decode('utf-8')
    err = yt_data_extract.extract_decryption_function(info, base_js)
    if err:
        return err
    err = yt_data_extract.decrypt_signatures(info)
    return err


def get_ordered_music_list_attributes(music_list):
    # get the set of attributes which are used by atleast 1 track
    # so there isn't an empty, extraneous album column which no tracks use, for example
    used_attributes = set()
    for track in music_list:
        used_attributes = used_attributes | track.keys()

    # now put them in the right order
    ordered_attributes = []
    for attribute in ('Artist', 'Title', 'Album'):
        if attribute.lower() in used_attributes:
            ordered_attributes.append(attribute)

    return ordered_attributes

headers = (
    ('Accept', '*/*'),
    ('Accept-Language', 'en-US,en;q=0.5'),
    ('X-YouTube-Client-Name', '2'),
    ('X-YouTube-Client-Version', '2.20180830'),
) + util.mobile_ua
def extract_info(video_id, use_invidious, playlist_id=None, index=None):
    # bpctr=9999999999 will bypass are-you-sure dialogs for controversial videos
    url = 'https://m.youtube.com/watch?v=' + video_id + '&pbj=1&bpctr=9999999999'
    if playlist_id:
        url += '&list=' + playlist_id
    if index:
        url += '&index=' + index
    polymer_json = util.fetch_url(url, headers=headers, debug_name='watch')

    # If there's a captcha... Return word Captcha
    if polymer_json == 'Captcha':
        return 'Captcha'

    polymer_json = polymer_json.decode('utf-8')
    # TODO: Decide whether this should be done in yt_data_extract.extract_watch_info
    try:
        polymer_json = json.loads(polymer_json)
    except json.decoder.JSONDecodeError:
        traceback.print_exc()
        return {'error': 'Failed to parse json response'}
    info = yt_data_extract.extract_watch_info(polymer_json)

    # age restriction bypass
    if info['age_restricted']:
        print('Fetching age restriction bypass page')
        data = {
            'video_id': video_id,
            'eurl': 'https://youtube.googleapis.com/v/' + video_id,
        }
        url = 'https://www.youtube.com/get_video_info?' + urllib.parse.urlencode(data)
        video_info_page = util.fetch_url(url, debug_name='get_video_info', report_text='Fetched age restriction bypass page').decode('utf-8')
        yt_data_extract.update_with_age_restricted_info(info, video_info_page)

    # signature decryption
    decryption_error = decrypt_signatures(info)
    if decryption_error:
        decryption_error = 'Error decrypting url signatures: ' + decryption_error
        info['playability_error'] = decryption_error
    # check if urls ready (non-live format) in former livestream
    # urls not ready if all of them have no filesize
    if info['was_live']:
        info['urls_ready'] = False
        for fmt in info['formats']:
            if fmt['file_size'] is not None:
                info['urls_ready'] = True
    else:
        info['urls_ready'] = True

    # livestream urls
    # sometimes only the livestream urls work soon after the livestream is over
    if (info['hls_manifest_url']
        and (info['live'] or not info['formats'] or not info['urls_ready'])
    ):
        manifest = util.fetch_url(info['hls_manifest_url'],
            debug_name='hls_manifest.m3u8',
            report_text='Fetched hls manifest'
        ).decode('utf-8')

        info['hls_formats'], err = yt_data_extract.extract_hls_formats(manifest)
        if not err:
            info['playability_error'] = None
        for fmt in info['hls_formats']:
            fmt['video_quality'] = video_quality_string(fmt)
    else:
        info['hls_formats'] = []

    # check for 403. Unnecessary for tor video routing b/c ip address is same
    info['invidious_used'] = False
    info['invidious_reload_button'] = False
    info['tor_bypass_used'] = False
    return info

def video_quality_string(format):
    if format['vcodec']:
        result =str(format['width'] or '?') + 'x' + str(format['height'] or '?')
        if format['fps']:
            result += ' ' + str(format['fps']) + 'fps'
        return result
    elif format['acodec']:
        return 'audio only'

    return '?'

def audio_quality_string(format):
    if format['acodec']:
        result = str(format['audio_bitrate'] or '?') + 'k'
        if format['audio_sample_rate']:
            result += ' ' + str(format['audio_sample_rate']) + ' Hz'
        return result
    elif format['vcodec']:
        return 'video only'

    return '?'

# from https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/utils.py
def format_bytes(bytes):
    if bytes is None:
        return 'N/A'
    if type(bytes) is str:
        bytes = float(bytes)
    if bytes == 0.0:
        exponent = 0
    else:
        exponent = int(math.log(bytes, 1024.0))
    suffix = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB'][exponent]
    converted = float(bytes) / float(1024 ** exponent)
    return '%.2f%s' % (converted, suffix)


