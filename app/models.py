from datetime import datetime
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

channel_association = db.Table('channel_association',
    db.Column('channel_id', db.String, db.ForeignKey('channel.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
) # Association: CHANNEL --followed by--> [USERS]

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # TWITTER    
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
    
    # YOUTUBE
    def youtube_following_list(self):
        return self.youtubeFollowed.all()
    
    def is_following_yt(self, cid):
        temp_cid = invidiousFollow.query.filter_by(channelId = cid).first()
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

    youtubeFollowed = db.relationship("invidiousFollow",
        secondary=channel_association,
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
    content = "El gato siguió a la liebre. Esto es un texto de ejemplo."
    profilePic = "url"
    timeStamp = "error"
    userProfilePic = "1.png"

class invidiousPost():
    channelName = 'Error'
    channelUrl = '#'
    videoUrl = '#'
    videoTitle = '#'
    videoThumb = '#'
    description = "LOREM IPSUM"
    date = 'None'
    views = 'NaN'
    id = 'isod'


class invidiousFollow(db.Model):
    __tablename__ = 'channel'
    id = db.Column(db.Integer, primary_key=True)
    channelId = db.Column(db.String(30), nullable=False, unique=True)
    followers = db.relationship('User', 
                                secondary=channel_association,
                                back_populates="youtubeFollowed")
    
    def __repr__(self):
        return '<invidiousFollow {}>'.format(self.channelId)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.String(100))
    url = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(24))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)