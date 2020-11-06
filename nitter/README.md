- [user.py](#userpy)
- [feed.py](#feedpy)
- [Tweets format examples](#tweets-format-examples)

## user.py

### get_user_info(username)
Returns the info of a particular Twitter user without tweets. If the user does not exist, it returns `False`.

##### Return example:

`user.get_user_info("Snowden")`
```
{
	'profileFullName': 'Edward Snowden',
	'profileUsername': '@Snowden',
	'profileBio': 'I used to work for the government. Now I work for the public. President at @FreedomofPress.',
	'tweets': '5,009',
	'following': '1',
	'followers': '4.41M',
	'likes': '473',
	'profilePic': 'https://nitter.net/pic/profile_images%2F648888480974508032%2F66_cUYfj.jpg'
}
```

### get_tweets(user, page=1)
Returns a list with the tweets on the user feed from the specified page (default is 1).

Example usage: `user.get_tweets("Snowden")`

### get_feed_tweets(html)
This function is used by `get_tweets`. This should not be used as it is a utility function. If you want to know more, you can explore the code.

## feed.py

### get_feed(usernames, daysMaxOld=10, includeRT=True)
This function returns a chronologically ordered feed given a list of usernames (i.e ['Snowden', 'DanielMicay', 'FluffyPony']). Optional parameters are:
* `daysMaxOld`: sets the maximum number of days that the feed posts that will be returned can be.
* `includeRT`: If `False` retweets will be excluded from the feed.

## Tweets format examples:
**Normal tweet**:
```
{
	'op': '@Snowden',
	'twitterName': 'Edward Snowden',
	'timeStamp': '2020-11-03 23:11:40',
	'date': 'Nov 3',
	'content': Markup('Vote. There is still time.'),
	'username': '@Snowden',
	'isRT': False,
	'profilePic': 'https://nitter.net/pic/profile_images%2F648888480974508032%2F66_cUYfj_normal.jpg',
	'url': 'https://nitter.net/Snowden/status/1323764814817218560#m'
}
```

**Retweet**:
```
{
	'op': '@StellaMoris1',
	'twitterName': 'Stella Moris',
	'timeStamp': '2020-11-02 10:21:09',
	'date': 'Nov 2',
	'content': Markup("Spoke to Julian. A friend of his killed himself in the early hours of this morning. His body is still in the cell on Julian's wing. Julian is devastated.\n\nManoel Santos was gay. He'd lived in UK for 20 years. The Home Office served him with a deportation notice to Brazil.(Thread)"),
	'username': ' Edward Snowden retweeted',
	'isRT': True,
	'profilePic': 'https://nitter.net/pic/profile_images%2F1303198488184975360%2FiH4BdNIT_normal.jpg',
	'url': 'https://nitter.net/StellaMoris1/status/1323208519315849217#m'
}
```

**Tweet / Retweet with images**:
```
{
	'op': '@Reuters',
	'twitterName': 'Reuters',
	'timeStamp': '2020-11-02 10:35:07',
	'date': 'Nov 2',
	'content': Markup('U.S. whistleblower Edward Snowden seeks Russian passport for sake of future son <a href="http://reut.rs/3mNZQuf">reut.rs/3mNZQuf</a>'),
	'username': ' Edward Snowden retweeted',
	'isRT': True,
	'profilePic': 'https://nitter.net/pic/profile_images%2F1194751949821939712%2F3VBu4_Sa_normal.jpg',
	'url': 'https://nitter.net/Reuters/status/1323212031978295298#m',
	'attachedImages': ['https://nitter.net/pic/media%2FElz-VKLWkAAvTf8.jpg%3Fname%3Dorig']
}
```

**Tweet quoting antoher user**
```
{
	'op': '@lsjourneys',
	'twitterName': 'Lsjourney',
	'timeStamp': '2020-10-28 21:17:09',
	'date': 'Oct 28',
	'content': Markup('citizenfive 👶'),
	'username': ' Edward Snowden retweeted',
	'isRT': True,
	'profilePic': 'https://nitter.net/pic/profile_images%2F647551437875101696%2FBA2I4vuf_normal.jpg',
	'url': 'https://nitter.net/lsjourneys/status/1321561665117310979#m',
	'isReply': True,
	'replyingTweetContent': Markup('<div class="quote-text">A long time in the making: our greatest collaboration is coming soon.</div>'),
	'replyAttachedImages': ['https://nitter.net/pic/media%2FElcdC-BXgAwtT79.jpg%3Fname%3Dorig'],
	'replyingUser': '@lsjourneys'
}
```

> Video is not fully supported yet. A parameter `'attachedVideo': True` is added when a video is present on the tweet.
