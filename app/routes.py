from flask_login import login_user, logout_user, current_user, login_required
from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, RegistrationForm, EmptyForm, SearchForm
from requests_futures.sessions import FuturesSession
from concurrent.futures import as_completed
from app.models import User, twitterPost, Post
from werkzeug.urls import url_parse
from bs4 import BeautifulSoup
from flask import Markup
from app import app, db
import time, datetime
import random, string
import feedparser
import requests

nitterInstance = "https://nitter.net/"
nitterInstanceII = "https://nitter.mastodont.cat"

@app.route('/')
@app.route('/index')
@login_required
def index():
    start_time = time.time()
    following = current_user.following_list()
    followed = current_user.followed.count()
    posts = []
    avatarPath = "img/avatars/1.png"
    form = EmptyForm()
    posts.extend(getFeed(following))
    posts.sort(key=lambda x: x.timeStamp, reverse=True)
    if not posts:
        profilePic = avatarPath
    else:
        profilePic = posts[0].userProfilePic
    print("--- {} seconds fetching feed---".format(time.time() - start_time))
    return render_template('index.html', title='Home', posts=posts, avatar=avatarPath, profilePic = profilePic, followedCount=followed, form=form)

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


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        if isTwitterUser(form.username.data):
            flash('This is username is taken! Choose a different one.')
        else:
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/savePost/<url>', methods=['POST'])
@login_required
def savePost(url):
    savedUrl = url.replace('~', '/')
    r = requests.get(savedUrl)
    html = BeautifulSoup(str(r.content), "lxml")
    post = html.body.find_all('div', attrs={'class':'tweet-content'})

    newPost = Post()
    newPost.url = savedUrl
    newPost.body = html.body.find_all('div', attrs={'class':'main-tweet'})[0].find_all('div', attrs={'class':'tweet-content'})[0].text
    newPost.username = html.body.find('a','username').text.replace("@","")
    newPost.timestamp = html.body.find_all('p', attrs={'class':'tweet-published'})[0].text
    newPost.user_id = current_user.id
    try:
        db.session.add(newPost)
        db.session.commit()
    except:
        flash("Post could not be saved. Either it was already saved or there was an error.")
    return redirect(url_for('index'))

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
        user = User.query.filter_by(username=username).first()
        isTwitter = isTwitterUser(username)
        if user is None and isTwitter:
            x = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
            newUser = User(username=username, email="{}@person.is".format(x))
            db.session.add(newUser)
            db.session.commit()
            flash('You are now following {}!'.format(username))
            #flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash('You are following {}!'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))

@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('You are no longer following {}.'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))

@app.route('/unfollowList/<username>', methods=['POST'])
@login_required
def unfollowList(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('You are no longer following {}!'.format(username))
        return redirect(url_for('following'))
    else:
        return redirect(url_for('index'))

@app.route('/following')
@login_required
def following():
    form = EmptyForm()
    following = current_user.following_list()
    followed = current_user.followed.count()
    return render_template('following.html', accounts = following, count = followed, form = form)

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    form = SearchForm()
    parsedResults = []
    if form.validate_on_submit():
        user = form.username.data
        r = requests.get("{instance}search?f=users&q={usern}".format(instance=nitterInstance, usern=user.replace(" ", "+")))
        html = BeautifulSoup(str(r.content), "lxml")
        results = html.body.find_all('a', attrs={'class':'tweet-link'})
        if results:
            parsedResults = [s['href'].replace("/", "") for s in results]
            return render_template('search.html', form = form, results = parsedResults)
        else:
            flash("User {} not found...".format(user))
            return render_template('search.html', form = form, results = parsedResults)
    else:
        return render_template('search.html', form = form)



@app.route('/error/<errno>')
def error(errno):
    return render_template('{}.html'.format(str(errno)))

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first()
    isTwitter = isTwitterUser(username)

    if isTwitter and user is None:
        x = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
        newUser = User(username=username, email="{}@person.is".format(x))
        db.session.add(newUser)
        db.session.commit()
    
    elif not isTwitter and user is None:
        return redirect( url_for('error', errno="404"))
    
    posts = []
    posts.extend(getPosts(username))
    form = EmptyForm()
    user = User.query.filter_by(username=username).first()
    if not posts:
        profilePic = avatarPath
    else:
        profilePic = posts[0].userProfilePic
    return render_template('user.html', user=user, posts=posts, profilePic = profilePic, form=form)

def getTimeDiff(t):
    tweetTime = datetime.datetime(*t[:6])
    diff = datetime.datetime.now() - tweetTime

    if diff.days == 0:
        if diff.seconds > 3599:
            timeString = "{}h".format(int((diff.seconds/60)/60))
        else:
            timeString = "{}m".format(int(diff.seconds/60))
    else:
        timeString = "{}d".format(diff.days)
    return timeString

def isTwitterUser(username):
    request = requests.get('https://nitter.net/{}/rss'.format(username), timeout=5)
    if request.status_code == 404:
        return False
    return True

def getFeed(urls):
    avatarPath = "img/avatars/{}.png".format(str(random.randint(1,12)))
    feedPosts = []
    with FuturesSession() as session:
        futures = [session.get('https://nitter.net/{}/rss'.format(u.username)) for u in urls]
        for future in as_completed(futures):
            resp = future.result()
            rssFeed=feedparser.parse(resp.content)
            if rssFeed.entries != []:
                    for post in rssFeed.entries:
                        newPost = twitterPost()
                        newPost.username = rssFeed.feed.title.split("/")[1].replace(" ", "")
                        newPost.twitterName = rssFeed.feed.title.split("/")[0]
                        newPost.date = getTimeDiff(post.published_parsed)
                        newPost.timeStamp = datetime.datetime(*post.published_parsed[:6])
                        newPost.op = post.author
                        try:
                            newPost.userProfilePic = rssFeed.channel.image.url
                        except:
                            newPost.profilePicture = ""
                        newPost.url = post.link
                        newPost.content = Markup(post.description)
                        
                        if "Pinned" in post.title.split(":")[0]:
                            newPost.isPinned = True

                        if "RT by" in post.title:
                            newPost.isRT = True
                            newPost.profilePic = ""
                        else:
                            newPost.isRT = False
                            try:
                                newPost.profilePic = rssFeed.channel.image.url
                            except:
                                newPost.profilePic = avatarPath
                        feedPosts.append(newPost)
    time.sleep(1)
    return feedPosts

def getPosts(account):
    avatarPath = "img/avatars/{}.png".format(str(random.randint(1,12)))
    posts = []
        
    #Gather profile info.
    rssFeed = feedparser.parse('{instance}{user}/rss'.format(instance=nitterInstance, user=account))
    #Gather posts
    if rssFeed.entries != []:
        for post in rssFeed.entries:
            newPost = twitterPost()
            newPost.username = rssFeed.feed.title.split("/")[1].replace(" ", "")
            newPost.twitterName = rssFeed.feed.title.split("/")[0]
            newPost.date = getTimeDiff(post.published_parsed)
            newPost.timeStamp = datetime.datetime(*post.published_parsed[:6])
            newPost.op = post.author
            try:
                newPost.userProfilePic = rssFeed.channel.image.url
            except:
                newPost.profilePicture = ""
            newPost.url = post.link
            newPost.content = Markup(post.description)
            
            if "Pinned" in post.title.split(":")[0]:
                newPost.isPinned = True

            if "RT by" in post.title:
                newPost.isRT = True
                newPost.profilePic = ""
            else:
                newPost.isRT = False
                try:
                    newPost.profilePic = rssFeed.channel.image.url
                except:
                    newPost.profilePic = avatarPath
            posts.append(newPost)
    return posts