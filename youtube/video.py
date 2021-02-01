from youtube_dlc import YoutubeDL
import json
options = {
    'ignoreerrors': True,
    'quiet': True,
    'skip_download': True
}
ydl = YoutubeDL(options)
ydl.add_default_info_extractors()
config = json.load(open('yotter-config.json'))

def get_info(url):
    video = {}
    video['error'] = False

    try:
        info = ydl.extract_info(url, download=False)
    except:
        video['error'] = True

    if info == None:
        video['error'] = True
    if not video['error'] and info is not None:
        video['uploader'] = info['uploader']
        video['uploader_id'] = info['uploader_id']
        video['channel_id'] = info['channel_id']
        video['upload_date'] = info['upload_date']
        video['title'] = info['title']
        video['thumbnails'] = info['thumbnails']
        video['description'] = info['description']
        video['categories'] = info['categories']
        video['subtitles'] = info['subtitles']
        video['duration'] = info['duration']
        video['view_count'] = info['view_count']

        if(info['like_count'] is None):
            video['like_count'] = 0
        else:
            video['like_count'] = int(info['like_count'])

        if(info['dislike_count'] is None):
            video['dislike_count'] = 0
        else:
            video['dislike_count'] = int(info['dislike_count'])

        video['total_likes'] = video['dislike_count'] + video['like_count']

        video['average_rating'] = str(info['average_rating'])[0:4]
        video['formats'] = get_video_formats(info['formats'])
        video['audio_formats'] = get_video_formats(info['formats'], audio=True)
        video['is_live'] = info['is_live']
        video['start_time'] = info['start_time']
        video['end_time'] = info['end_time']
        video['series'] = info['series']
        video['subscriber_count'] = info['subscriber_count']
    return video

def get_video_formats(formats, audio=False):
    best_formats = []
    audio_formats = []
    for format in formats:
        if format['vcodec'] != 'none' and format['acodec'] != 'none':
            # Video and Audio
            if format['format_note'] == '144p':
                continue
            else:
                best_formats.append(format)
        elif format['vcodec'] == 'none' and format['acodec'] != 'none':
            # Audio only
            audio_formats.append(format)
        else:
            # Video only
            continue

    if audio:
        return audio_formats
    else:
        return best_formats
