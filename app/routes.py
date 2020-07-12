from flask_login import login_user, logout_user, current_user, login_required
from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, RegistrationForm, EmptyForm
from app.models import User, twitterPost
from werkzeug.urls import url_parse
from flask import Markup
from app import app, db
import time, datetime
import random, string
import feedparser

@app.route('/')
@app.route('/index')
@login_required
def index():
    following = current_user.following_list()
    followed = current_user.followed.count()
    posts = []
    avatarPath = "img/avatars/1.png"
    for fwd in following:
        avatarPath = "img/avatars/{}.png".format(str(random.randint(1,12)))
        
        #Gather profile info.
        rssFeed = feedparser.parse('https://nitter.net/{}/rss'.format(fwd.username))

        #Gather posts
        if rssFeed.entries != []:
            for post in rssFeed.entries:
                newPost = twitterPost()

                newPost.profilePic = rssFeed.channel.image.url
                newPost.twitterAt = rssFeed.feed.title.split("/")[1].replace(" ", "")
                newPost.twitterName = rssFeed.feed.title.split("/")[0]

                newPost.username = rssFeed.feed.title.split("/")[0]
                newPost.date = getTimeDiff(post.published_parsed)
                newPost.timeStamp = datetime.datetime(*post.published_parsed[:6])
                newPost.op = post.author
                newPost.urlToPost = post.link
                newPost.content = Markup(post.description)

                if "RT by" in post.title:
                    newPost.isRT = True
                else:
                    newPost.isRT = False
                posts.append(newPost)
        posts.sort(key=lambda x: x.timeStamp, reverse=True)
    return render_template('index.html', title='Home', posts=posts, avatar=avatarPath, followedCount = followed)


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
        rssFeed = feedparser.parse('https://nitter.net/{}/rss'.format(form.username.data))

        if rssFeed.entries == []:
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('login'))
        else:
            flash('This is username is taken! Choose a different one.')
    return render_template('register.html', title='Register', form=form)

@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        isTwitter = True
        if user is None and isTwitter:
            x = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
            newUser = User(username=username, email="{}@person.is".format(x))
            print(x)
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
        flash('You are not following {}.'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first()
    isTwitter = True
    if user is None and isTwitter:
        x = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
        newUser = User(username=username, email="{}@person.is".format(x))
        db.session.add(newUser)
        db.session.commit()
        #flash('User {} not found.'.format(username))
    
    #Gather profile info.
    rssFeed = feedparser.parse('https://nitter.net/{}/rss'.format(username))

    #Gather posts
    posts = []
    for post in rssFeed.entries:
        newPost = twitterPost()

        newPost.profilePic = rssFeed.channel.image.url
        newPost.twitterAt = rssFeed.feed.title.split("/")[1].replace(" ", "")
        newPost.twitterName = rssFeed.feed.title.split("/")[0]

        newPost.username = rssFeed.feed.title.split("/")[0]
        newPost.date = getTimeDiff(post.published_parsed)
        newPost.timeStamp = datetime.datetime(*post.published_parsed[:6])
        newPost.op = post.author
        newPost.urlToPost = post.link
        newPost.content = Markup(post.description)

        if "RT by" in post.title:
            newPost.isRT = True
        else:
            newPost.isRT = False

        #validPost = True
        posts.append(newPost)

    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts, form=form, profilePic=rssFeed.channel.image.url)

def getTimeDiff(t):
    today = datetime.datetime.now()
    tweetTime = datetime.datetime(*t[:6])
    diff = today - tweetTime
    timeString = "0m"

    if diff.days == 0:
        minutes = diff.seconds/60
        if minutes > 60:
            hours = minutes/60
            timeString = "{}h".format(hours)
        else:
            timeString = "{}m".format(minutes)
    else:
        timeString = "{}d".format(diff.days)
    return timeString