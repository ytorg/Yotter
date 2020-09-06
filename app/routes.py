from flask import render_template, flash, redirect, url_for, request, send_from_directory, Markup
from app.forms import LoginForm, RegistrationForm, EmptyForm, SearchForm, ChannelForm
from app.models import User, twitterPost, ytPost, Post, youtubeFollow, twitterFollow
from flask_login import login_user, logout_user, current_user, login_required
from flask import Flask, Response, stream_with_context
from requests_futures.sessions import FuturesSession
from werkzeug.datastructures import Headers
from concurrent.futures import as_completed
from werkzeug.utils import secure_filename
from youtube_search import YoutubeSearch
from werkzeug.urls import url_parse
from youtube_dl import YoutubeDL
from numerize import numerize
from bs4 import BeautifulSoup
from xml.dom import minidom
from app import app, db
from re import findall
import random, string
import time, datetime
import feedparser
import requests
import bleach
import urllib
import json
import re
##########################
#### Config variables ####
##########################
config = json.load(open('yotter-config.json'))
##########################
#### Config variables ####
##########################
NITTERINSTANCE = config['nitterInstance'] # Must be https://.../ 
YOUTUBERSS = "https://www.youtube.com/feeds/videos.xml?channel_id="

##########################
#### Global variables ####
##########################
ALLOWED_EXTENSIONS = {'json', 'db'}

#########################
#### Twitter Logic ######
#########################
@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('home.html')

@app.route('/twitter')
@login_required
def twitter():
    start_time = time.time()
    followingList = current_user.twitter_following_list()
    followCount = len(followingList)
    posts = []
    avatarPath = "img/avatars/1.png"
    form = EmptyForm()
    posts.extend(getFeed(followingList))
    posts.sort(key=lambda x: x.timeStamp, reverse=True)
    if not posts:
        profilePic = avatarPath
    else:
        profilePic = posts[0].userProfilePic
    print("--- {} seconds fetching twitter feed---".format(time.time() - start_time))
    return render_template('twitter.html', title='Yotter | Twitter', posts=posts, avatar=avatarPath, profilePic = profilePic, followedCount=followCount, form=form)

@app.route('/savePost/<url>', methods=['POST'])
@login_required
def savePost(url):
    savedUrl = url.replace('~', '/')
    r = requests.get(savedUrl)
    html = BeautifulSoup(str(r.content), "lxml")
    post = html.body.find('div', attrs={'class':'main-tweet'})

    newPost = Post()
    newPost.url = savedUrl
    newPost.username = post.find('a','username').text.replace("@","")
    newPost.body = post.find_all('div', attrs={'class':'tweet-content'})[0].text.encode('latin1').decode('unicode_escape').encode('latin1').decode('utf8')
    newPost.timestamp = post.find_all('p', attrs={'class':'tweet-published'})[0].text.encode('latin1').decode('unicode_escape').encode('latin1').decode('utf8')
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
    return render_template('saved.html', title='Saved', savedPosts=savedPosts)

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
    return render_template('following.html', accounts = accounts, count = followCount, form = form)

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    form = SearchForm()
    if form.validate_on_submit():
        user = form.username.data
        results = twitterUserSearch(user)
        if results:
            return render_template('search.html', form = form, results = results)
        else:
            flash("User {} not found...".format(user))
            return redirect(request.referrer)
    else:
        return render_template('search.html', form = form)

@app.route('/u/<username>')
@login_required
def u(username):
    form = EmptyForm() 
    avatarPath = "img/avatars/{}.png".format(str(random.randint(1,12)))
    user = getTwitterUserInfo(username)
    if not user:
        flash("This user is not on Twitter.")
        return redirect(request.referrer)
    
    posts = []
    posts.extend(getPosts(username))
    if not posts:
        user['profilePic'] = avatarPath

    return render_template('user.html', posts=posts, user=user, form=form)

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
    return render_template('youtube.html', title="Yotter | Youtube", videos=videos, followCount=followCount)

@app.route('/ytfollowing', methods=['GET', 'POST'])
@login_required
def ytfollowing():
    form = EmptyForm()
    channelList = current_user.youtube_following_list()
    channelCount = len(channelList)
    
    return render_template('ytfollowing.html', form=form, channelList=channelList, channelCount=channelCount)

@app.route('/ytsearch', methods=['GET', 'POST'])
@login_required
def ytsearch():
    form = ChannelForm()
    button_form = EmptyForm()
    if form.validate_on_submit():
        channels = []
        videos = []

        searchTerm = form.channelId.data
        search = YoutubeSearch(searchTerm)
        chnns = search.channels_to_dict()
        vids = search.videos_to_dict()
        
        for v in vids:
            videos.append({
                'channelName':v['channel'],
                'videoTitle':v['title'],
                'description':Markup(v['long_desc']),
                'id':v['id'],
                'videoThumb': v['thumbnails'][-1],
                'channelUrl':v['url_suffix'],
                'channelId': v['channelId'],
                'views':v['views'],
                'timeStamp':v['publishedText']
            })

        for c in chnns:
            channels.append({
                'username':c['name'],
                'channelId':c['id'],
                'thumbnail':'https:{}'.format(c['thumbnails'][0]),
                'subCount':c['suscriberCountText'].split(" ")[0]
            })
        return render_template('ytsearch.html', form=form, btform=button_form, channels=channels, videos=videos)

    else:
        return render_template('ytsearch.html', form=form)

@app.route('/ytfollow/<channelId>', methods=['POST'])
@login_required
def ytfollow(channelId):
    form = EmptyForm()
    if form.validate_on_submit():
        r = followYoutubeChannel(channelId)            
    return redirect(request.referrer)

def followYoutubeChannel(channelId):
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
    except:
        flash("Youtube: Couldn't follow {}. Already followed?".format(channelData[0]['name']))
        return False

@app.route('/ytunfollow/<channelId>', methods=['POST'])
@login_required
def ytunfollow(channelId):
    form = EmptyForm()
    if form.validate_on_submit():
        r =  unfollowYoutubeChannel(channelId)
    return redirect(request.referrer)

def unfollowYoutubeChannel(channelId):
    try:
        channel = youtubeFollow.query.filter_by(channelId=channelId).first()
        db.session.delete(channel)
        db.session.commit()
        flash("{} unfollowed!".format(channel.channelName))
    except:
        flash("There was an error unfollowing the user. Try again.")
    return redirect(request.referrer)

@app.route('/channel/<id>', methods=['GET'])
@app.route('/user/<id>', methods=['GET'])
@login_required
def channel(id):
    form = ChannelForm()
    button_form = EmptyForm()
    data = requests.get('https://www.youtube.com/feeds/videos.xml?channel_id={id}'.format(id=id))
    data = feedparser.parse(data.content)

    channelData = YoutubeSearch.channelInfo(id)
    return render_template('channel.html', form=form, btform=button_form, channel=channelData[0], videos=channelData[1])

@app.route('/watch', methods=['GET'])
@login_required
def watch():
    id = request.args.get('v', None)
    ydl = YoutubeDL()
    data = ydl.extract_info(id, False)
    if data['formats'][-1]['url'].find("manifest.googlevideo") > 0:
        flash("Livestreams are not yet supported!")
        return redirect(url_for('youtube'))

    video = {
        'title':data['title'],
        'description':Markup(markupString(data['description'])),
        'viewCount':data['view_count'],
        'author':data['uploader'],
        'authorUrl':data['uploader_url'],
        'channelId': data['uploader_id'],
        'id':id,
        'averageRating': str((float(data['average_rating'])/5)*100)
    }
    return render_template("video.html", video=video)

def markupString(string):
    string = string.replace("\n\n", "<br><br>").replace("\n", "<br>")
    string = bleach.linkify(string)
    string = string.replace("https://youtube.com/", "")
    string = string.replace("https://www.youtube.com/", "")
    string = string.replace("https://twitter.com/", "/u/")
    return string

## PROXY videos through Yotter server to the client.
@app.route('/stream', methods=['GET', 'POST'])
@login_required
def stream():
    #This function proxies the video stream from GoogleVideo to the client.
    id = request.args.get('v', None)
    headers = Headers()    
    if(id):
        ydl = YoutubeDL()
        data = ydl.extract_info("{id}".format(id=id), download=False)
        req = requests.get(data['formats'][-1]['url'], stream = True)
        headers.add('Accept-Ranges','bytes')
        headers.add('Content-Length', str(int(req.headers['Content-Length'])+1))
        response = Response(req.iter_content(chunk_size=1024*1024), mimetype=req.headers['Content-Type'], content_type=req.headers['Content-Type'], direct_passthrough=True, headers=headers)
        #enable browser file caching with etags
        response.cache_control.public  = True
        response.cache_control.max_age = int(60000)
        return response
    else:
        flash("Something went wrong loading the video... Try again.")
        return redirect(url_for('youtube'))

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
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

#Proxy images through server
@app.route('/img/<url>', methods=['GET', 'POST'])
@login_required
def img(url):
    pic = requests.get(url.replace("~", "/"))
    return Response(pic,mimetype="image/png")

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/settings')
@login_required
def settings():
    instanceInfo = {
        "totalUsers":db.session.query(User).count(),
        "location":config['serverLocation'],
        "serverName":config['serverName']
    }
    return render_template('settings.html', info=instanceInfo)

@app.route('/export')
@login_required
#Export data into a JSON file. Later you can import the data.
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
        if file and allowed_file(file.filename) or 'subscription_manager' in file.filename:
            option = request.form['import_format']
            if option == 'yotter':
                importYotterSubscriptions(file)
            elif option == 'newpipe':
                importNewPipeSubscriptions(file)
            elif option == 'youtube':
                importYoutubeSubscriptions(file)
            elif option == 'freetube':
                importFreeTubeSubscriptions(file)
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


def importYotterSubscriptions(file):
    filename = secure_filename(file.filename)
    data = json.load(file)
    for acc in data['twitter']:
        r = followTwitterAccount(acc['username'])
    
    for acc in data['youtube']:
        r = followYoutubeChannel(acc['channelId'])

def importNewPipeSubscriptions(file):
    filename = secure_filename(file.filename)
    data = json.load(file)
    for acc in data['subscriptions']:
        r = followYoutubeChannel(re.search('(UC[a-zA-Z0-9_-]{22})|(?<=user\/)[a-zA-Z0-9_-]+', acc['url']).group())

def importYoutubeSubscriptions(file):
    filename = secure_filename(file.filename)
    itemlist = minidom.parse(file).getElementsByTagName('outline')
    for item in itemlist[1:]:
        r = followYoutubeChannel(re.search('UC[a-zA-Z0-9_-]{22}', item.attributes['xmlUrl'].value).group())

def importFreeTubeSubscriptions(file):
    filename = secure_filename(file.filename)
    data = re.findall('UC[a-zA-Z0-9_-]{22}', file.read().decode('utf-8'))
    for acc in data:
        r = followYoutubeChannel(acc)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        
    return render_template('register.html', title='Register', registrations=REGISTRATIONS, form=form)

@app.route('/error/<errno>')
def error(errno):
    return render_template('{}.html'.format(str(errno)))

def getTimeDiff(t):
    diff = datetime.datetime.now() - datetime.datetime(*t[:6])

    if diff.days == 0:
        if diff.seconds > 3599:
            timeString = "{}h".format(int((diff.seconds/60)/60))
        else:
            timeString = "{}m".format(int(diff.seconds/60))
    else:
        timeString = "{}d".format(diff.days)
    return timeString

def isTwitterUser(username):
    response = requests.get('{instance}{user}/rss'.format(instance=NITTERINSTANCE, user=username))
    if response.status_code == 404:
        return False
    return True

def twitterUserSearch(terms):
    
    response = urllib.request.urlopen('{instance}search?f=users&q={user}'.format(instance=NITTERINSTANCE, user=urllib.parse.quote(terms))).read()
    html = BeautifulSoup(str(response), "lxml")

    results = []
    if html.body.find('h2', attrs={'class':'timeline-none'}):
        return False
    else:
        html = html.body.find_all('div', attrs={'class':'timeline-item'})
        for item in html:
            user = {
                "fullName": item.find('a', attrs={'class':'fullname'}).getText().encode('latin_1').decode('unicode_escape').encode('latin_1').decode('utf8'),
                "username": item.find('a', attrs={'class':'username'}).getText().encode('latin_1').decode('unicode_escape').encode('latin_1').decode('utf8'),
                'avatar': "{i}{s}".format(i=NITTERINSTANCE, s=item.find('img', attrs={'class':'avatar'})['src'][1:])
            }
            results.append(user)
        return results


def getTwitterUserInfo(username):
    response = urllib.request.urlopen('{instance}{user}'.format(instance=NITTERINSTANCE, user=username)).read()
    #rssFeed = feedparser.parse(response.content)

    html = BeautifulSoup(str(response), "lxml")
    if html.body.find('div', attrs={'class':'error-panel'}):
        return False
    else:
        html = html.body.find('div', attrs={'class':'profile-card'})

        if html.find('a', attrs={'class':'profile-card-fullname'}):
            fullName = html.find('a', attrs={'class':'profile-card-fullname'}).getText().encode('latin1').decode('unicode_escape').encode('latin1').decode('utf8')
        else:
            fullName = None
        
        if html.find('div', attrs={'class':'profile-bio'}):
            profileBio = html.find('div', attrs={'class':'profile-bio'}).getText().encode('latin1').decode('unicode_escape').encode('latin1').decode('utf8')
        else:
            profileBio = None

        user = {
            "profileFullName":fullName,
            "profileUsername":html.find('a', attrs={'class':'profile-card-username'}).string.encode('latin_1').decode('unicode_escape').encode('latin_1').decode('utf8'),
            "profileBio":profileBio,
            "tweets":html.find_all('span', attrs={'class':'profile-stat-num'})[0].string,
            "following":html.find_all('span', attrs={'class':'profile-stat-num'})[1].string,
            "followers":numerize.numerize(int(html.find_all('span', attrs={'class':'profile-stat-num'})[2].string.replace(",",""))),
            "likes":html.find_all('span', attrs={'class':'profile-stat-num'})[3].string,
            "profilePic":"{instance}{pic}".format(instance=NITTERINSTANCE, pic=html.find('a', attrs={'class':'profile-card-avatar'})['href'][1:])
        }
        return user

def getFeed(urls):
    feedPosts = []
    with FuturesSession() as session:
        futures = [session.get('{instance}{user}'.format(instance=NITTERINSTANCE, user=u.username)) for u in urls]
        for future in as_completed(futures):
            res = future.result().content.decode('utf-8')
            html = BeautifulSoup(res, "html.parser")
            userFeed = html.find_all('div', attrs={'class':'timeline-item'})
            if userFeed != []:
                    for post in userFeed[:-1]:
                        date_time_str = post.find('span', attrs={'class':'tweet-date'}).find('a')['title'].replace(",","")
                        time = datetime.datetime.now() - datetime.datetime.strptime(date_time_str, '%d/%m/%Y %H:%M:%S')
                        if time.days >=7:
                            continue

                        if post.find('div', attrs={'class':'pinned'}):
                            if post.find('div', attrs={'class':'pinned'}).find('span', attrs={'icon-pin'}):
                                continue

                        newPost = twitterPost()
                        newPost.op = post.find('a', attrs={'class':'username'}).text
                        newPost.twitterName = post.find('a', attrs={'class':'fullname'}).text
                        newPost.timeStamp = datetime.datetime.strptime(date_time_str, '%d/%m/%Y %H:%M:%S')
                        newPost.date = post.find('span', attrs={'class':'tweet-date'}).find('a').text
                        newPost.content = Markup(post.find('div',  attrs={'class':'tweet-content'}))
                        
                        if post.find('div', attrs={'class':'retweet-header'}):
                            newPost.username = post.find('div', attrs={'class':'retweet-header'}).find('div', attrs={'class':'icon-container'}).text
                            newPost.isRT = True
                        else:
                            newPost.username = newPost.op
                            newPost.isRT = False
                        
                        newPost.profilePic = NITTERINSTANCE+post.find('a', attrs={'class':'tweet-avatar'}).find('img')['src'][1:]
                        newPost.url = NITTERINSTANCE + post.find('a', attrs={'class':'tweet-link'})['href'][1:]
                        if post.find('div', attrs={'class':'quote'}):
                            newPost.isReply = True
                            quote = post.find('div', attrs={'class':'quote'})
                            if quote.find('div',  attrs={'class':'quote-text'}):
                                newPost.replyingTweetContent = Markup(quote.find('div',  attrs={'class':'quote-text'}))
                                
                            if quote.find('a', attrs={'class':'still-image'}):
                                newPost.replyAttachedImg = NITTERINSTANCE+quote.find('a', attrs={'class':'still-image'})['href'][1:]
                            
                            newPost.replyingUser=quote.find('a',  attrs={'class':'username'}).text
                            post.find('div', attrs={'class':'quote'}).decompose()

                        if post.find('div',  attrs={'class':'attachments'}):
                            if not post.find(class_='quote'):
                                if  post.find('div',  attrs={'class':'attachments'}).find('a', attrs={'class':'still-image'}):
                                    newPost.attachedImg = NITTERINSTANCE + post.find('div',  attrs={'class':'attachments'}).find('a')['href'][1:]
                        feedPosts.append(newPost)
    return feedPosts

def getPosts(account):
    feedPosts = []
        
    #Gather profile info.
    rssFeed = urllib.request.urlopen('{instance}{user}'.format(instance=NITTERINSTANCE, user=account)).read()
    #Gather feedPosts
    res = rssFeed.decode('utf-8')
    html = BeautifulSoup(res, "html.parser")
    userFeed = html.find_all('div', attrs={'class':'timeline-item'})
    if userFeed != []:
            for post in userFeed[:-1]:
                date_time_str = post.find('span', attrs={'class':'tweet-date'}).find('a')['title'].replace(",","")
                time = datetime.datetime.now() - datetime.datetime.strptime(date_time_str, '%d/%m/%Y %H:%M:%S')

                if post.find('div', attrs={'class':'pinned'}):
                    if post.find('div', attrs={'class':'pinned'}).find('span', attrs={'icon-pin'}):
                        continue

                newPost = twitterPost()
                newPost.op = post.find('a', attrs={'class':'username'}).text
                newPost.twitterName = post.find('a', attrs={'class':'fullname'}).text
                newPost.timeStamp = datetime.datetime.strptime(date_time_str, '%d/%m/%Y %H:%M:%S')
                newPost.date = post.find('span', attrs={'class':'tweet-date'}).find('a').text
                newPost.content = Markup(post.find('div',  attrs={'class':'tweet-content'}))
                
                if post.find('div', attrs={'class':'retweet-header'}):
                    newPost.username = post.find('div', attrs={'class':'retweet-header'}).find('div', attrs={'class':'icon-container'}).text
                    newPost.isRT = True
                else:
                    newPost.username = newPost.op
                    newPost.isRT = False
                
                newPost.profilePic = NITTERINSTANCE+post.find('a', attrs={'class':'tweet-avatar'}).find('img')['src'][1:]
                newPost.url = NITTERINSTANCE + post.find('a', attrs={'class':'tweet-link'})['href'][1:]
                if post.find('div', attrs={'class':'quote'}):
                    newPost.isReply = True
                    quote = post.find('div', attrs={'class':'quote'})
                    if quote.find('div',  attrs={'class':'quote-text'}):
                        newPost.replyingTweetContent = Markup(quote.find('div',  attrs={'class':'quote-text'}))
                        
                    if quote.find('a', attrs={'class':'still-image'}):
                        newPost.replyAttachedImg = NITTERINSTANCE+quote.find('a', attrs={'class':'still-image'})['href'][1:]
                    
                    newPost.replyingUser=quote.find('a',  attrs={'class':'username'}).text
                    post.find('div', attrs={'class':'quote'}).decompose()

                if post.find('div',  attrs={'class':'attachments'}):
                    if not post.find(class_='quote'):
                        if  post.find('div',  attrs={'class':'attachments'}).find('a', attrs={'class':'still-image'}):
                            newPost.attachedImg = NITTERINSTANCE + post.find('div',  attrs={'class':'attachments'}).find('a')['href'][1:]
                feedPosts.append(newPost)
    return feedPosts

def getYoutubePosts(ids):
    videos = []
    with FuturesSession() as session:
        futures = [session.get('https://www.youtube.com/feeds/videos.xml?channel_id={id}'.format(id=id.channelId)) for id in ids]
        for future in as_completed(futures):
            resp = future.result()
            rssFeed=feedparser.parse(resp.content)
            for vid in rssFeed.entries:
                time = datetime.datetime.now() - datetime.datetime(*vid.published_parsed[:6])

                if time.days >=7:
                    continue
                
                video = ytPost()
                video.date = vid.published_parsed
                video.timeStamp = getTimeDiff(vid.published_parsed)
                video.channelName = vid.author_detail.name
                video.channelId = vid.yt_channelid
                video.channelUrl = vid.author_detail.href
                video.id = vid.yt_videoid
                video.videoTitle = vid.title
                video.videoThumb = vid.media_thumbnail[0]['url'].replace('/', '~')
                video.views = vid.media_statistics['views']
                video.description = vid.summary_detail.value
                video.description = re.sub(r'^https?:\/\/.*[\r\n]*', '', video.description[0:120]+"...", flags=re.MULTILINE)
                videos.append(video)
    return videos
