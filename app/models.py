from datetime import datetime
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

channel_association = db.Table('channel_association',
    db.Column('channel_id', db.Integer, db.ForeignKey('channel.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
) # Association: CHANNEL --followed by--> [USERS]

twitter_association = db.Table('twitter_association',
    db.Column('account_id', db.Integer, db.ForeignKey('twitterAccount.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
) # Association: ACCOUNT --followed by--> [USERS]

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow())
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_last_seen(self):
        self.last_seen = datetime.utcnow()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0
    
    def following_list(self):
        return self.followed.all()

    def saved_posts(self):
        return Post.query.filter_by(user_id=self.id)

    # TWITTER
    def twitter_following_list(self):
        return self.twitterFollowed.all()
    
    def is_following_tw(self, uname):
        temp_cid = twitterFollow.query.filter_by(username = uname).first()
        if temp_cid is None:
            return False
        else:
            following = self.twitter_following_list()
            for f in following:
                if f.username == uname:
                    return True
        return False
    
    # YOUTUBE
    def youtube_following_list(self):
        return self.youtubeFollowed.all()
    
    def is_following_yt(self, cid):
        temp_cid = youtubeFollow.query.filter_by(channelId = cid).first()
        if temp_cid is None:
            return False
        else:
            following = self.youtube_following_list()
            for f in following:
                if f.channelId == cid:
                    return True
        return False
        
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    youtubeFollowed = db.relationship("youtubeFollow",
        secondary=channel_association,
        back_populates="followers",
        lazy='dynamic')

    twitterFollowed = db.relationship("twitterFollow",
        secondary=twitter_association,
        back_populates="followers",
        lazy='dynamic')


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class twitterPost():
    date = 0
    username = 'Error'
    twitterName = "Error Name"
    isPinned = False
    op = 'Error'
    isRT = True
    urlToPost = ""
    validPost = True
    content = ""
    profilePic = "url"
    timeStamp = "error"
    userProfilePic = "1.png"
    isReply = False
    replyingUrl = "#"
    replyingUser = "@nobody"
    replyingTweetContent = ""
    attachedImg = ""
    replyAttachedImg = ""

class ytPost():
    channelName = 'Error'
    channelUrl = '#'
    channelId = '@'
    videoUrl = '#'
    videoTitle = '#'
    videoThumb = '#'
    description = "LOREM IPSUM"
    date = 'None'
    views = 'NaN'
    id = 'isod'


class youtubeFollow(db.Model):
    __tablename__ = 'channel'
    id = db.Column(db.Integer, primary_key=True)
    channelId = db.Column(db.String(30), nullable=False)
    channelName = db.Column(db.String(30))
    followers = db.relationship('User', 
                                secondary=channel_association,
                                back_populates="youtubeFollowed")
    
    def __repr__(self):
        return '<youtubeFollow {}>'.format(self.channelName)

class twitterFollow(db.Model):
    __tablename__ = 'twitterAccount'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False)
    followers = db.relationship('User', 
                                secondary=twitter_association,
                                back_populates="twitterFollowed")
    
    def __repr__(self):
        return '<twitterFollow {}>'.format(self.username)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.String(100))
    url = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(24))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)
        
