import datetime
import glob
import json
import math
import os
import random
import re
import time
import urllib
from concurrent.futures import as_completed

import bleach
import feedparser
import requests
from bs4 import BeautifulSoup
from flask import Response
from flask import render_template, flash, redirect, url_for, request, send_from_directory, Markup
from flask_caching import Cache
from flask_login import login_user, logout_user, current_user, login_required
from numerize import numerize
from requests_futures.sessions import FuturesSession
from werkzeug.datastructures import Headers
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from youtube_search import YoutubeSearch

from app import app, db
from app.forms import LoginForm, RegistrationForm, EmptyForm, SearchForm, ChannelForm
from app.models import User, twitterPost, ytPost, Post, youtubeFollow, twitterFollow
from youtube import comments, utils, channel as ytch, search as yts
from youtube import watch as ytwatch

#########################################

#########################################

cache = Cache(config={'CACHE_TYPE': 'simple'})
cache.init_app(app)
##########################
#### Config variables ####
##########################
config = json.load(open('yotter-config.json'))
##########################
#### Config variables ####
##########################
NITTERINSTANCE = config['nitterInstance']  # Must be https://.../
YOUTUBERSS = "https://www.youtube.com/feeds/videos.xml?channel_id="


##########################
#### Global variables ####
##########################

#########################
#### Twitter Logic ######
#########################
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.set_last_seen()
        db.session.commit()


@app.route('/')
@app.route('/index')
@login_required
@cache.cached(timeout=50, key_prefix='home')
def index():
    return render_template('home.html', config=config)


@app.route('/twitter')
@app.route('/twitter/<page>')
@login_required
def twitter(page=0):
    followingList = current_user.twitter_following_list()
    form = EmptyForm()
    followCount = len(followingList)
    page = int(page)
    avatarPath = "img/avatars/1.png"
    posts = []

    cache_file = glob.glob("app/cache/{}_*".format(current_user.username))
    if (len(cache_file) > 0):
        time_diff = round(time.time() - os.path.getmtime(cache_file[0]))
    else:
        time_diff = 999
    # If cache file is more than 1 minute old
    if page == 0 and time_diff > 60:
        if cache_file:
            for f in cache_file:
                os.remove(f)
        feed = getFeed(followingList)
        cache_file = "{u}_{d}.json".format(u=current_user.username, d=time.strftime("%Y%m%d-%H%M%S"))
        with open("app/cache/{}".format(cache_file), 'w') as fp:
            json.dump(feed, fp)
    # Else, refresh feed
    else:
        try:
            cache_file = glob.glob("app/cache/{}*".format(current_user.username))[0]
            with open(cache_file, 'r') as fp:
                feed = json.load(fp)
        except:
            feed = getFeed(followingList)
            cache_file = "{u}_{d}.json".format(u=current_user.username, d=time.strftime("%Y%m%d-%H%M%S"))
            with open("app/cache/{}".format(cache_file), 'w') as fp:
                json.dump(feed, fp)

    posts.extend(feed)
    posts.sort(key=lambda x: datetime.datetime.strptime(x['timeStamp'], '%d/%m/%Y %H:%M:%S'), reverse=True)

    # Items range per page
    page_items = page * 16
    offset = page_items + 16
    # Pagination logic
    init_page = page - 3
    if init_page < 0:
        init_page = 0
    total_pages = page + 5
    max_pages = int(math.ceil(len(posts) / 10))  # Total number of pages.
    if total_pages > max_pages:
        total_pages = max_pages

    # Posts to render
    if posts and len(posts) > offset:
        posts = posts[page_items:offset]
    else:
        posts = posts[page_items:]

    if not posts:
        profilePic = avatarPath
    else:
        profilePic = posts[0]['profilePic']
    return render_template('twitter.html', title='Yotter | Twitter', posts=posts, avatar=avatarPath,
                           profilePic=profilePic, followedCount=followCount, form=form, config=config,
                           pages=total_pages, init_page=init_page, actual_page=page)


@app.route('/savePost/<url>', methods=['POST'])
@login_required
def savePost(url):
    savedUrl = url.replace('~', '/')
    r = requests.get(savedUrl)
    html = BeautifulSoup(str(r.content), "lxml")
    post = html.body.find('div', attrs={'class': 'main-tweet'})

    newPost = Post()
    newPost.url = savedUrl
    newPost.username = post.find('a', 'username').text.replace("@", "")
    newPost.body = post.find_all('div', attrs={'class': 'tweet-content'})[0].text.encode('latin1').decode(
        'unicode_escape').encode('latin1').decode('utf8')
    newPost.timestamp = post.find_all('p', attrs={'class': 'tweet-published'})[0].text.encode('latin1').decode(
        'unicode_escape').encode('latin1').decode('utf8')
    newPost.user_id = current_user.id
    try:
        db.session.add(newPost)
        db.session.commit()
    except:
        flash("Post could not be saved. Either it was already saved or there was an error.")
    return redirect(request.referrer)


@app.route('/saved')
@login_required
def saved():
    savedPosts = current_user.saved_posts().all()
    return render_template('saved.html', title='Saved', savedPosts=savedPosts, config=config)


@app.route('/deleteSaved/<id>', methods=['POST'])
@login_required
def deleteSaved(id):
    savedPost = Post.query.filter_by(id=id).first()
    db.session.delete(savedPost)
    db.session.commit()
    return redirect(url_for('saved'))


@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        if followTwitterAccount(username):
            flash("{} followed!".format(username))
    return redirect(request.referrer)


def followTwitterAccount(username):
    if isTwitterUser(username):
        if not current_user.is_following_tw(username):
            try:
                follow = twitterFollow()
                follow.username = username
                follow.followers.append(current_user)
                db.session.add(follow)
                db.session.commit()
                return True
            except:
                flash("Twitter: Couldn't follow {}. Already followed?".format(username))
                return False
    else:
        flash("Something went wrong... try again")
        return False


@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        if twUnfollow(username):
            flash("{} unfollowed!".format(username))
    return redirect(request.referrer)


def twUnfollow(username):
    try:
        user = twitterFollow.query.filter_by(username=username).first()
        db.session.delete(user)
        db.session.commit()
    except:
        flash("There was an error unfollowing the user. Try again.")
    return redirect(request.referrer)


@app.route('/following')
@login_required
def following():
    form = EmptyForm()
    followCount = len(current_user.twitter_following_list())
    accounts = current_user.twitter_following_list()
    return render_template('following.html', accounts=accounts, count=followCount, form=form, config=config)


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    form = SearchForm()
    if form.validate_on_submit():
        user = form.username.data
        results = twitterUserSearch(user)
        if results:
            return render_template('search.html', form=form, results=results, config=config)
        else:
            flash("User {} not found...".format(user))
            return redirect(request.referrer)
    else:
        return render_template('search.html', form=form, config=config)


@app.route('/u/<username>')
@app.route('/<username>')
@login_required
def u(username):
    if username == "favicon.ico":
        return redirect(url_for('static', filename='favicons/favicon.ico'))
    form = EmptyForm()
    avatarPath = "img/avatars/{}.png".format(str(random.randint(1, 12)))
    user = getTwitterUserInfo(username)
    if not user:
        flash("This user is not on Twitter.")
        return redirect(request.referrer)

    posts = []
    posts.extend(getPosts(username))
    if not posts:
        user['profilePic'] = avatarPath

    return render_template('user.html', posts=posts, user=user, form=form, config=config)


#########################
#### Youtube Logic ######
#########################
@app.route('/youtube', methods=['GET', 'POST'])
@login_required
def youtube():
    followCount = len(current_user.youtube_following_list())
    start_time = time.time()
    ids = current_user.youtube_following_list()
    videos = getYoutubePosts(ids)
    if videos:
        videos.sort(key=lambda x: x.date, reverse=True)
    print("--- {} seconds fetching youtube feed---".format(time.time() - start_time))
    return render_template('youtube.html', title="Yotter | Youtube", videos=videos, followCount=followCount,
                           config=config)


@app.route('/ytfollowing', methods=['GET', 'POST'])
@login_required
def ytfollowing():
    form = EmptyForm()
    channelList = current_user.youtube_following_list()
    channelCount = len(channelList)

    return render_template('ytfollowing.html', form=form, channelList=channelList, channelCount=channelCount,
                           config=config)


@app.route('/ytsearch', methods=['GET', 'POST'])
@login_required
def ytsearch():
    form = ChannelForm()
    button_form = EmptyForm()
    query = request.args.get('q', None)
    sort = request.args.get('s', None)
    if sort != None:
        sort = int(sort)
    else:
        sort = 0

    page = request.args.get('p', None)
    if page == None:
        page = 1

    if query:
        autocorrect = 1
        filters = {"time": 0, "type": 0, "duration": 0}
        results = yts.search_by_terms(query, page, autocorrect, sort, filters)

        next_page = "/ytsearch?q={q}&s={s}&p={p}".format(q=query, s=sort, p=int(page) + 1)
        if int(page) == 1:
            prev_page = "/ytsearch?q={q}&s={s}&p={p}".format(q=query, s=sort, p=1)
        else:
            prev_page = "/ytsearch?q={q}&s={s}&p={p}".format(q=query, s=sort, p=int(page) - 1)

        for video in results['videos']:
            hostname = urllib.parse.urlparse(video['videoThumb']).netloc
            video['videoThumb'] = video['videoThumb'].replace("https://{}".format(hostname), "") + "&host=" + hostname

        for channel in results['channels']:
            if config['nginxVideoStream']:
                channel['thumbnail'] = channel['thumbnail'].replace("~", "/")
                hostName = urllib.parse.urlparse(channel['thumbnail']).netloc
                channel['thumbnail'] = channel['thumbnail'].replace("https://{}".format(hostName),
                                                                    "") + "?host=" + hostName
        return render_template('ytsearch.html', form=form, btform=button_form, results=results,
                               restricted=config['restrictPublicUsage'], config=config, npage=next_page,
                               ppage=prev_page)
    else:
        return render_template('ytsearch.html', form=form, results=False)


@app.route('/ytfollow/<channelId>', methods=['POST'])
@login_required
def ytfollow(channelId):
    r = followYoutubeChannel(channelId)
    return redirect(request.referrer)


def followYoutubeChannel(channelId):
    try:
        channelData = YoutubeSearch.channelInfo(channelId, False)
        try:
            if not current_user.is_following_yt(channelId):
                follow = youtubeFollow()
                follow.channelId = channelId
                follow.channelName = channelData[0]['name']
                follow.followers.append(current_user)
                db.session.add(follow)
                db.session.commit()
                flash("{} followed!".format(channelData[0]['name']))
                return True
            else:
                return False
        except Exception as e:
            print(e)
            flash("Youtube: Couldn't follow {}. Already followed?".format(channelData[0]['name']))
            return False
    except KeyError as ke:
        print("KeyError: {}:'{}' could not be found".format(ke, channelId))
        flash("Youtube: ChannelId '{}' is not valid".format(channelId))
        return False


@app.route('/ytunfollow/<channelId>', methods=['POST'])
@login_required
def ytunfollow(channelId):
    unfollowYoutubeChannel(channelId)
    return redirect(request.referrer)


def unfollowYoutubeChannel(channelId):
    try:
        channel = youtubeFollow.query.filter_by(channelId=channelId).first()
        name = channel.channelName
        db.session.delete(channel)
        db.session.commit()
        channel = youtubeFollow.query.filter_by(channelId=channelId).first()
        if channel:
            db.session.delete(channel)
            db.session.commit()
        flash("{} unfollowed!".format(name))
    except:
        flash("There was an error unfollowing the user. Try again.")


@app.route('/channel/<id>', methods=['GET'])
@app.route('/user/<id>', methods=['GET'])
@app.route('/c/<id>', methods=['GET'])
@login_required
def channel(id):
    form = ChannelForm()
    button_form = EmptyForm()

    page = request.args.get('p', None)
    sort = request.args.get('s', None)
    if page is None:
        page = 1
    if sort is None:
        sort = 3

    data = ytch.get_channel_tab_info(id, page, sort)

    for video in data['items']:
        if config['nginxVideoStream']:
            hostName = urllib.parse.urlparse(video['thumbnail'][1:]).netloc
            video['thumbnail'] = video['thumbnail'].replace("https://{}".format(hostName), "")[1:].replace("hqdefault",
                                                                                                       "mqdefault") + "&host=" + hostName
        else:
            video['thumbnail'] = video['thumbnail'].replace('/', '~')

    if config['nginxVideoStream']:
        hostName = urllib.parse.urlparse(data['avatar'][1:]).netloc
        data['avatar'] = data['avatar'].replace("https://{}".format(hostName), "")[1:] + "?host=" + hostName
    else:
        data['avatar'] = data['avatar'].replace('/', '~')

    next_page = "/channel/{q}?s={s}&p={p}".format(q=id, s=sort, p=int(page) + 1)
    if int(page) == 1:
        prev_page = "/channel/{q}?s={s}&p={p}".format(q=id, s=sort, p=1)
    else:
        prev_page = "/channel/{q}?s={s}&p={p}".format(q=id, s=sort, p=int(page) - 1)

    return render_template('channel.html', form=form, btform=button_form, data=data,
                           restricted=config['restrictPublicUsage'], config=config, next_page=next_page, prev_page=prev_page)


def get_best_urls(urls):
    '''Gets URLS in youtube format (format_id, url, height) and returns best ones for yotter'''
    best_formats = ["22", "18", "34", "35", "36", "37", "38", "43", "44", "45", "46"]
    best_urls = []
    for url in urls:
        for f in best_formats:
            if url['format_id'] == f:
                best_urls.append(url)
    return best_urls


def get_live_urls(urls):
    """Gets URLS in youtube format (format_id, url, height) and returns best ones for yotter"""
    best_formats = ["91", "92", "93", "94", "95", "96"]
    best_urls = []
    for url in urls:
        for f in best_formats:
            if url['format_id'] == f:
                best_urls.append(url)
    return best_urls


@app.route('/watch', methods=['GET'])
@login_required
def watch():
    id = request.args.get('v', None)
    info = ytwatch.extract_info(id, False, playlist_id=None, index=None)

    vsources = ytwatch.get_video_sources(info, False)
    # Retry 3 times if no sources are available.
    retry = 3
    while retry != 0 and len(vsources) == 0:
        vsources = ytwatch.get_video_sources(info, False)
        retry -= 1

    for source in vsources:
        hostName = urllib.parse.urlparse(source['src']).netloc
        source['src'] = source['src'].replace("https://{}".format(hostName), "") + "&host=" + hostName

    # Parse video formats
    for v_format in info['formats']:
        hostName = urllib.parse.urlparse(v_format['url']).netloc
        v_format['url'] = v_format['url'].replace("https://{}".format(hostName), "") + "&host=" + hostName
        if v_format['audio_bitrate'] is not None and v_format['vcodec'] is None:
            v_format['audio_valid'] = True

    # Markup description
    info['description'] = Markup(bleach.linkify(info['description'].replace("\n", "<br>")))

    # Get comments
    videocomments = comments.video_comments(id, sort=0, offset=0, lc='', secret_key='')
    videocomments = utils.post_process_comments_info(videocomments)
    if videocomments is not None:
        videocomments.sort(key=lambda x: x['likes'], reverse=True)

    # Calculate rating %
    info['rating'] = str((info['like_count'] / (info['like_count'] + info['dislike_count'])) * 100)[0:4]
    return render_template("video.html", info=info, title='{}'.format(info['title']), config=config,
                           videocomments=videocomments, vsources=vsources)


def markupString(string):
    string = string.replace("\n\n", "<br><br>").replace("\n", "<br>")
    string = bleach.linkify(string)
    string = string.replace("https://youtube.com/", "")
    string = string.replace("https://www.youtube.com/", "")
    string = string.replace("https://twitter.com/", "/u/")
    return Markup(string)


## PROXY videos through Yotter server to the client.
@app.route('/stream/<url>', methods=['GET', 'POST'])
@login_required
def stream(url):
    # This function proxies the video stream from GoogleVideo to the client.
    url = url.replace('YotterSlash', '/')
    headers = Headers()
    if (url):
        s = requests.Session()
        s.verify = True
        req = s.get(url, stream=True)
        headers.add('Range', request.headers['Range'])
        headers.add('Accept-Ranges', 'bytes')
        headers.add('Content-Length', str(int(req.headers['Content-Length']) + 1))
        response = Response(req.iter_content(chunk_size=10 * 1024), mimetype=req.headers['Content-Type'],
                            content_type=req.headers['Content-Type'], direct_passthrough=True, headers=headers)
        # enable browser file caching with etags
        response.cache_control.public = True
        response.cache_control.max_age = int(60000)
        return response
    else:
        flash("Something went wrong loading the video... Try again.")
        return redirect(url_for('youtube'))


def download_file(streamable):
    with streamable as stream:
        stream.raise_for_status()
        for chunk in stream.iter_content(chunk_size=8192):
            yield chunk


#########################
#### General Logic ######
#########################
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        if user.username == config['admin_user']:
            user.set_admin_user()
            db.session.commit()
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form, config=config)


# Proxy images through server
@app.route('/img/<url>', methods=['GET', 'POST'])
@login_required
def img(url):
    pic = requests.get(url.replace("~", "/"))
    return Response(pic, mimetype="image/png")


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/settings')
@login_required
@cache.cached(timeout=50, key_prefix='settings')
def settings():
    active = 0
    users = db.session.query(User).all()
    for u in users:
        if u.last_seen == None:
            u.set_last_seen()
            db.session.commit()
        else:
            t = datetime.datetime.utcnow() - u.last_seen
            s = t.total_seconds()
            m = s / 60
            if m < 25:
                active = active + 1

    instanceInfo = {
        "totalUsers": db.session.query(User).count(),
        "active": active,
    }
    return render_template('settings.html', info=instanceInfo, config=config, admin=current_user.is_admin)


'''@app.route('/clear_inactive_users/<phash>')
@login_required
def clear_inactive_users(phash):
    ahash = User.query.filter_by(username=config['admin_user']).first().password_hash
    if phash == ahash:
        users = db.session.query(User).all()
        for u in users:
            if u.username == config['admin_user']:
                continue
            t = datetime.datetime.utcnow() - u.last_seen
            t = math.floor(t.total_seconds())
            max_old_s = config['max_old_user_days']*86400
            if t > max_old_s:
                user = User.query.filter_by(username=u.username).first()
                print("deleted "+u.username)
                db.session.delete(user)
                db.session.commit()
    else:
        flash("You must be admin for this action")
    return redirect(request.referrer)'''


@app.route('/export')
@login_required
# Export data into a JSON file. Later you can import the data.
def export():
    a = exportData()
    if a:
        return send_from_directory('.', 'data_export.json', as_attachment=True)
    else:
        return redirect(url_for('error/405'))


def exportData():
    twitterFollowing = current_user.twitter_following_list()
    youtubeFollowing = current_user.youtube_following_list()
    data = {}
    data['twitter'] = []
    data['youtube'] = []

    for f in twitterFollowing:
        data['twitter'].append({
            'username': f.username
        })

    for f in youtubeFollowing:
        data['youtube'].append({
            'channelId': f.channelId
        })

    try:
        with open('app/data_export.json', 'w') as outfile:
            json.dump(data, outfile)
        return True
    except:
        return False


@app.route('/importdata', methods=['GET', 'POST'])
@login_required
def importdata():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.referrer)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.referrer)
        else:
            option = request.form['import_format']
            if option == 'yotter':
                importYotterSubscriptions(file)
            elif option == 'youtube':
                importYoutubeSubscriptions(file)
            return redirect(request.referrer)

    return redirect(request.referrer)


@app.route('/deleteme', methods=['GET', 'POST'])
@login_required
def deleteme():
    user = User.query.filter_by(username=current_user.username).first()
    db.session.delete(user)
    db.session.commit()
    logout_user()
    return redirect(url_for('index'))


def importYoutubeSubscriptions(file):
    filename = secure_filename(file.filename)
    try:
        data = re.findall('(UC[a-zA-Z0-9_-]{22})|(?<=user/)[a-zA-Z0-9_-]+', file.read().decode('utf-8'))
        for acc in data:
            r = followYoutubeChannel(acc)
    except Exception as e:
        print(e)
        flash("File is not valid.")


def importYotterSubscriptions(file):
    filename = secure_filename(file.filename)
    data = json.load(file)
    for acc in data['twitter']:
        r = followTwitterAccount(acc['username'])

    for acc in data['youtube']:
        r = followYoutubeChannel(acc['channelId'])


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    REGISTRATIONS = True
    try:
        count = db.session.query(User).count()
        if count >= config['maxInstanceUsers'] or config['maxInstanceUsers'] == 0:
            REGISTRATIONS = False
    except:
        REGISTRATIONS = True

    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash("This username is taken! Try with another.")
            return redirect(request.referrer)

        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', registrations=REGISTRATIONS, form=form, config=config)


@app.route('/registrations_status/icon')
def registrations_status_icon():
    count = db.session.query(User).count()
    if count >= config['maxInstanceUsers'] or config['maxInstanceUsers'] == 0:
        return redirect(url_for('static', filename='img/close.png'))
    else:
        return redirect(url_for('static', filename='img/open.png'))


@app.route('/registrations_status/text')
def registrations_status_text():
    count = db.session.query(User).count()
    return "{c}/{t}".format(c=count, t=config['maxInstanceUsers'])


@app.route('/error/<errno>')
def error(errno):
    return render_template('{}.html'.format(str(errno)), config=config)


def getTimeDiff(t):
    diff = datetime.datetime.now() - datetime.datetime(*t[:6])

    if diff.days == 0:
        if diff.seconds > 3599:
            timeString = "{}h".format(int((diff.seconds / 60) / 60))
        else:
            timeString = "{}m".format(int(diff.seconds / 60))
    else:
        timeString = "{}d".format(diff.days)
    return timeString


def isTwitterUser(username):
    response = requests.get('{instance}{user}/rss'.format(instance=NITTERINSTANCE, user=username))
    if response.status_code == 404:
        return False
    return True


def twitterUserSearch(terms):
    response = urllib.request.urlopen(
        '{instance}search?f=users&q={user}'.format(instance=NITTERINSTANCE, user=urllib.parse.quote(terms))).read()
    html = BeautifulSoup(str(response), "lxml")

    results = []
    if html.body.find('h2', attrs={'class': 'timeline-none'}):
        return False
    else:
        html = html.body.find_all('div', attrs={'class': 'timeline-item'})
        for item in html:
            user = {
                "fullName": item.find('a', attrs={'class': 'fullname'}).getText().encode('latin_1').decode(
                    'unicode_escape').encode('latin_1').decode('utf8'),
                "username": item.find('a', attrs={'class': 'username'}).getText().encode('latin_1').decode(
                    'unicode_escape').encode('latin_1').decode('utf8'),
                'avatar': "{i}{s}".format(i=NITTERINSTANCE, s=item.find('img', attrs={'class': 'avatar'})['src'][1:])
            }
            results.append(user)
        return results


def getTwitterUserInfo(username):
    response = urllib.request.urlopen('{instance}{user}'.format(instance=NITTERINSTANCE, user=username)).read()
    # rssFeed = feedparser.parse(response.content)

    html = BeautifulSoup(str(response), "lxml")
    if html.body.find('div', attrs={'class': 'error-panel'}):
        return False
    else:
        html = html.body.find('div', attrs={'class': 'profile-card'})

        if html.find('a', attrs={'class': 'profile-card-fullname'}):
            fullName = html.find('a', attrs={'class': 'profile-card-fullname'}).getText().encode('latin1').decode(
                'unicode_escape').encode('latin1').decode('utf8')
        else:
            fullName = None

        if html.find('div', attrs={'class': 'profile-bio'}):
            profileBio = html.find('div', attrs={'class': 'profile-bio'}).getText().encode('latin1').decode(
                'unicode_escape').encode('latin1').decode('utf8')
        else:
            profileBio = None

        user = {
            "profileFullName": fullName,
            "profileUsername": html.find('a', attrs={'class': 'profile-card-username'}).string.encode('latin_1').decode(
                'unicode_escape').encode('latin_1').decode('utf8'),
            "profileBio": profileBio,
            "tweets": html.find_all('span', attrs={'class': 'profile-stat-num'})[0].string,
            "following": html.find_all('span', attrs={'class': 'profile-stat-num'})[1].string,
            "followers": numerize.numerize(
                int(html.find_all('span', attrs={'class': 'profile-stat-num'})[2].string.replace(",", ""))),
            "likes": html.find_all('span', attrs={'class': 'profile-stat-num'})[3].string,
            "profilePic": "{instance}{pic}".format(instance=NITTERINSTANCE,
                                                   pic=html.find('a', attrs={'class': 'profile-card-avatar'})['href'][
                                                       1:])
        }
        return user


def getFeed(urls):
    feedPosts = []
    with FuturesSession() as session:
        futures = [session.get('{instance}{user}'.format(instance=NITTERINSTANCE, user=u.username)) for u in urls]
        for future in as_completed(futures):
            res = future.result().content.decode('utf-8')
            html = BeautifulSoup(res, "html.parser")
            userFeed = html.find_all('div', attrs={'class': 'timeline-item'})
            if userFeed != []:
                for post in userFeed[:-1]:
                    date_time_str = post.find('span', attrs={'class': 'tweet-date'}).find('a')['title'].replace(",", "")
                    time = datetime.datetime.now() - datetime.datetime.strptime(date_time_str, '%d/%m/%Y %H:%M:%S')
                    if time.days >= 7:
                        continue

                    if post.find('div', attrs={'class': 'pinned'}):
                        if post.find('div', attrs={'class': 'pinned'}).find('span', attrs={'icon-pin'}):
                            continue

                    newPost = {}
                    newPost["op"] = post.find('a', attrs={'class': 'username'}).text
                    newPost["twitterName"] = post.find('a', attrs={'class': 'fullname'}).text
                    newPost["timeStamp"] = date_time_str
                    newPost["date"] = post.find('span', attrs={'class': 'tweet-date'}).find('a').text
                    newPost["content"] = Markup(post.find('div', attrs={'class': 'tweet-content'}))

                    if post.find('div', attrs={'class': 'retweet-header'}):
                        newPost["username"] = post.find('div', attrs={'class': 'retweet-header'}).find('div', attrs={
                            'class': 'icon-container'}).text
                        newPost["isRT"] = True
                    else:
                        newPost["username"] = newPost["op"]
                        newPost["isRT"] = False

                    newPost["profilePic"] = NITTERINSTANCE + \
                                            post.find('a', attrs={'class': 'tweet-avatar'}).find('img')['src'][1:]
                    newPost["url"] = NITTERINSTANCE + post.find('a', attrs={'class': 'tweet-link'})['href'][1:]
                    if post.find('div', attrs={'class': 'quote'}):
                        newPost["isReply"] = True
                        quote = post.find('div', attrs={'class': 'quote'})
                        if quote.find('div', attrs={'class': 'quote-text'}):
                            newPost["replyingTweetContent"] = Markup(quote.find('div', attrs={'class': 'quote-text'}))

                        if quote.find('a', attrs={'class': 'still-image'}):
                            newPost["replyAttachedImg"] = NITTERINSTANCE + \
                                                          quote.find('a', attrs={'class': 'still-image'})['href'][1:]

                        if quote.find('div', attrs={'class': 'unavailable-quote'}):
                            newPost["replyingUser"] = "Unavailable"
                        else:
                            try:
                                newPost["replyingUser"] = quote.find('a', attrs={'class': 'username'}).text
                            except:
                                newPost["replyingUser"] = "Unavailable"
                        post.find('div', attrs={'class': 'quote'}).decompose()

                    if post.find('div', attrs={'class': 'attachments'}):
                        if not post.find(class_='quote'):
                            if post.find('div', attrs={'class': 'attachments'}).find('a',
                                                                                     attrs={'class': 'still-image'}):
                                newPost["attachedImg"] = NITTERINSTANCE + \
                                                         post.find('div', attrs={'class': 'attachments'}).find('a')[
                                                             'href'][1:]
                    feedPosts.append(newPost)
    return feedPosts


def getPosts(account):
    feedPosts = []

    # Gather profile info.
    rssFeed = urllib.request.urlopen('{instance}{user}'.format(instance=NITTERINSTANCE, user=account)).read()
    # Gather feedPosts
    res = rssFeed.decode('utf-8')
    html = BeautifulSoup(res, "html.parser")
    userFeed = html.find_all('div', attrs={'class': 'timeline-item'})
    if userFeed != []:
        for post in userFeed[:-1]:
            date_time_str = post.find('span', attrs={'class': 'tweet-date'}).find('a')['title'].replace(",", "")

            if post.find('div', attrs={'class': 'pinned'}):
                if post.find('div', attrs={'class': 'pinned'}).find('span', attrs={'icon-pin'}):
                    continue

            newPost = twitterPost()
            newPost.op = post.find('a', attrs={'class': 'username'}).text
            newPost.twitterName = post.find('a', attrs={'class': 'fullname'}).text
            newPost.timeStamp = datetime.datetime.strptime(date_time_str, '%d/%m/%Y %H:%M:%S')
            newPost.date = post.find('span', attrs={'class': 'tweet-date'}).find('a').text
            newPost.content = Markup(post.find('div', attrs={'class': 'tweet-content'}))

            if post.find('div', attrs={'class': 'retweet-header'}):
                newPost.username = post.find('div', attrs={'class': 'retweet-header'}).find('div', attrs={
                    'class': 'icon-container'}).text
                newPost.isRT = True
            else:
                newPost.username = newPost.op
                newPost.isRT = False

            newPost.profilePic = NITTERINSTANCE + post.find('a', attrs={'class': 'tweet-avatar'}).find('img')['src'][1:]
            newPost.url = NITTERINSTANCE + post.find('a', attrs={'class': 'tweet-link'})['href'][1:]
            if post.find('div', attrs={'class': 'quote'}):
                newPost.isReply = True
                quote = post.find('div', attrs={'class': 'quote'})
                if quote.find('div', attrs={'class': 'quote-text'}):
                    newPost.replyingTweetContent = Markup(quote.find('div', attrs={'class': 'quote-text'}))

                if quote.find('a', attrs={'class': 'still-image'}):
                    newPost.replyAttachedImg = NITTERINSTANCE + quote.find('a', attrs={'class': 'still-image'})['href'][
                                                                1:]

                try:
                    newPost.replyingUser = quote.find('a', attrs={'class': 'username'}).text
                except:
                    newPost.replyingUser = "Unavailable"
                post.find('div', attrs={'class': 'quote'}).decompose()

            if post.find('div', attrs={'class': 'attachments'}):
                if not post.find(class_='quote'):
                    if post.find('div', attrs={'class': 'attachments'}).find('a', attrs={'class': 'still-image'}):
                        newPost.attachedImg = NITTERINSTANCE + \
                                              post.find('div', attrs={'class': 'attachments'}).find('a')['href'][1:]
            feedPosts.append(newPost)
    return feedPosts


def getYoutubePosts(ids):
    videos = []
    with FuturesSession() as session:
        futures = [session.get('https://www.youtube.com/feeds/videos.xml?channel_id={id}'.format(id=id.channelId)) for
                   id in ids]
        for future in as_completed(futures):
            resp = future.result()
            rssFeed = feedparser.parse(resp.content)
            for vid in rssFeed.entries:
                try:
                    # Try to get time diff
                    time = datetime.datetime.now() - datetime.datetime(*vid.published_parsed[:6])
                except:
                    # If youtube rss does not have parsed time, generate it. Else set time to 0.
                    try:
                        time = datetime.datetime.now() - datetime.datetime(
                            datetime.datetime.strptime(vid.published, '%y-%m-%dT%H:%M:%S+00:00'))
                    except:
                        time = datetime.datetime.now() - datetime.datetime.now()

                if time.days >= 6:
                    continue

                video = ytPost()
                try:
                    video.date = vid.published_parsed
                except:
                    try:
                        video.date = datetime.datetime.strptime(vid.published, '%y-%m-%dT%H:%M:%S+00:00').timetuple()
                    except:
                        video.date = datetime.datetime.utcnow().timetuple()
                try:
                    video.timeStamp = getTimeDiff(vid.published_parsed)
                except:
                    if time != 0:
                        video.timeStamp = "{} days".format(str(time.days))
                    else:
                        video.timeStamp = "Unknown"

                video.channelName = vid.author_detail.name
                video.channelId = vid.yt_channelid
                video.channelUrl = vid.author_detail.href
                video.id = vid.yt_videoid
                video.videoTitle = vid.title
                if config['nginxVideoStream']:
                    hostName = urllib.parse.urlparse(vid.media_thumbnail[0]['url']).netloc
                    video.videoThumb = vid.media_thumbnail[0]['url'].replace("https://{}".format(hostName), "").replace(
                        "hqdefault", "mqdefault") + "?host=" + hostName
                else:
                    video.videoThumb = vid.media_thumbnail[0]['url'].replace('/', '~')
                video.views = vid.media_statistics['views']
                video.description = vid.summary_detail.value
                video.description = re.sub(r'^https?:\/\/.*[\r\n]*', '', video.description[0:120] + "...",
                                           flags=re.MULTILINE)
                videos.append(video)
    return videos
