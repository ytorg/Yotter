<p align="center"> <img width="700" src="app/static/img/banner.png"> </img></p> 
<p align="center">
   <a href="https://www.gnu.org/licenses/gpl-3.0"><img alt="License: GPL v3" src="https://img.shields.io/badge/License-AGPLv3-blue.svg"></img></a>
   <a href="https://github.com/pluja/Yotter"><img alt="Development state" src="https://img.shields.io/badge/State-Beta-blue.svg"></img></a>
   <a href="https://github.com/pluja/Yotter/pulls"><img alt="Pull Requests Welcome" src="https://img.shields.io/badge/PRs-Welcome-green.svg"></img></a>
   <a href="https://github.com/pluja/Yotter/tree/master"><img alt="Formerly named Parasitter" src="https://img.shields.io/badge/Formerly-Parasitter-blue.svg"></img></a>
</p> 

Yotter allows you to follow and gather all the content from your favorite Twitter and YouTube accounts in a *beautiful* feed so you can stay up to date without compromising your privacy at all. Yotter is written with Python and Flask and uses Semantic-UI as its CSS framework.

Yotter is possible thanks to several open-source projects that are listed on the [Powered by](#powered-by) section. Make sure to check out those awesome projects!

# Index:
* [Why](#why)
* [Features](#features)
* [Screenshots](#screenshots)
* [Privacy and Security](#privacy)
* [Public instances](#public-instances)
* [Self hosting](https://github.com/ytorg/Yotter/blob/dev-indep/SELF-HOSTING.md)
    * [Update the server](https://github.com/ytorg/Yotter/blob/dev-indep/SELF-HOSTING.md#updating-the-server)
    * [Configure server](#configure-the-server)
* [Contributing and contact](#contributing)
* [Powered by](#powered-by)
* [Donate](#donate)

# Why
At first I started working on this project as a solution for following Twitter accounts (a thing that can't be done with Nitter) and getting a Twitter-like feed. Weeks later the leader of Invidious, Omar Roth, announced that he was stepping away from the project. As an Invidious active user, this made me think that a new alternative was needed for the community and also an alternative with an easier language for most people (as Invidious is written in Crystal). So I started developing a 'written-in-python Invidious alternative' and it went quite well.

I hope that this project can prosperate, gain contributors, new instances and create a good community around it.

# Features:
- [x] No Ads.
- [x] No Javascript needed*
- [x] Minimalist.
- [x] Search on Twitter and Youtube.
- [x] Zero connections to Google/Twitter on the client.
- [x] Follow Twitter accounts.
- [x] Follow Youtube accounts.
- [x] Play Youtube videos on background on Android.
- [x] Play only audio from youtube to save data.
- [x] Save your favourite Tweets.
- [x] Tor-friendly.
- [x] Terminal-browser friendly.

*Video player is VideoJS, which uses JavaScript. But if JavaScript is disabled Yotter still works perfectly and uses the default HTML video player.
> And many more to come!

# Privacy
#### Connections
Yotter cares about your privacy, and for this it will never make any connection to Twitter or Youtube on the client. Every request is proxied through the Yotter server; video streaming, photos, data gathering, scrapping, etc.

The Yotter server connects to Google (Youtube) and Nitter in order to gather all the necessary data. Then it serves it (proxyed through itself) to the client. This means that as a client, you will never connect to Google - the Yotter server will do it for you. So if you want to set up a Yotter server for privacy reasons I recommend you to set it up on a remote VPS so you don't share your IP with Google or use a VPN on the server. 

If you don't mind exposing your IP making requests to Google then you can set it up wherever you want. Even with this method you will **avoid all trackers, ads, heavy-loaded pages, etc**. - Even with this method, you can stay safe if you use a VPN to hide your IP.

#### Your data
The only things the database stores are:
* Hash of the password
* Username
* List of followed users
* List of saved posts
* Some user configurations (Dark theme, etc)

This data will never be used for any other purpose than offering the service to the user. It's not sent anywhere, never.

#### Security
Only the hash of your password is stored on the database. Also, no personal information of any kind is required nor kept, if a hacker gets access to the database the only thing they could do would be to follow/unfollow some accounts. So there's no motivation in 'hacking' Yotter.

I always recommend self-hosting, as you will be the only person with access to the data.

> Important note: The **client** never connects to Google / Youtube however, the server does in order to gather all the necessary things!

# Public Instances
| name |server location|max users|registrations|
| ------------ | ------------ | ------------ |------------|
| https://yotter.xyz  |Germany| 70 users|<img src="https://yotter.xyz/registrations_status/icon?1" width="17">|
| https://yotter.kavin.rocks/  |India| 100 users |<img src="https://yotter.kavin.rocks/registrations_status/icon?1" width="15">|
| https://yotter.jank.media/  |Germany| 100 users|<img src="https://yotter.jank.media/registrations_status/icon?1" width="15">|

## Configure the server
You will find in the root folder of the project a file named `yotter-config.json`. This is the global config file for the Yotter server.

Currently available config is:
* **serverName**: Name of the server. Format: `example.com`
* **nitterInstance**: Nitter instance that will be used when fetching Twitter content. Format must be `https://<NitterInstance.tld>/`
* **maxInstanceUsers**: Max users on the instance. When set to `0` it closes registrations.
* **serverLocation**: Location of the server.
* **restrictPublicUsage**: When set to `false` the instance allows non-registered users to use some routes (i.e /watch?v=..., /ytsearch, /channel...). See [this section](https://github.com/pluja/Yotter/blob/dev-indep/SELF-HOSTING.md#removing-log-in-restrictions)
* **nginxVideoStream**: Wether or not to use Nginx as streaming engine. It is recommended for public instances. [See this link]()
* **maintenance_mode**: Activates a message on the server warning users of maintenance mode.
* **show_admin_message**: Shows a message from the admin with title as `admin_message_title` and body as `admin_message`
* **admin_user**: Username of the admin user.
* **max_old_user_days**: Maximum days for a user to be inactive, otherwise will be deleted if admin uses the action.
* **donation_url**: Adds a link to a donation method for the instance.

# Contributing
Contributors are always welcome. You can help in many ways: Coding, organizing, designing, [donating](#donate), maintaining... You choose what you want to help with!

We have a [Matrix](https://matrix.org/) room where we discuss anything related with Yotter, feel free to enter the room and start talking or reading. You can choose a Matrix client from [this list of Matrix clients](https://matrix.org/clients/). Also you will need to choose an instance to host your account, you can find Matrix instances [here](https://www.hello-matrix.net/public_servers.php).

<a href="https://matrix.to/#/!wqJnbUtEfitxtOsLFj:privacytools.io?via=privacytools.io&via=matrix.org"><img alt="Join Matrix" src="https://img.shields.io/badge/Join Room-Matrix-black.svg">
   
 #### Other platforms:
 <a href="https://reddit.com/r/Yotter"><img alt="Join Matrix" src="https://img.shields.io/badge/Reddit-r/Yotter-orange.svg">

# Powered by:
* [Nitter](https://nitter.net/)
* [youtube-dl](https://github.com/ytdl-org/youtube-dl)
* [Flask](https://flask.palletsprojects.com/)
* [SQLAlchemy](https://docs.sqlalchemy.org/en/13/)
* [Semantic-UI](https://semantic-ui.com)
* [requests-futures](https://github.com/ross/requests-futures)
* [microblog](https://github.com/miguelgrinberg/microblog)
* [Video.js](https://videojs.com/)
* [My fork of youtube_search](https://github.com/pluja/youtube_search-fork)
* [Youtube-local](https://github.com/user234683/youtube-local)

# Donate
This project is completely free and Open Source and will always be.

Funding will be used 100% for opening and mantaining an online public instance of Yotter, this will be hosted on Netcup and will (at first) be the *VPS 500 G8*. I mention all of this in case you want to check the prices.
#### Crypto (preferred):
- **Bitcoin**: `bc1q5y3g907ju0pt40me7dr9fy5uhfhfgfv9k3kh3z`
- **Monero**: `48nQGAXaC6eFK2Wo7SVVyF9xL333gDHjzdmRL3XETEqbU3w4CcKjjHVUZPU4W3dg1oJL8be3iGtUAQsgV88dzbS7QNpZjC2`
#### Fiat:
- <a href="https://liberapay.com/pluja/donate"><img alt="Donate using Liberapay" src="https://liberapay.com/assets/widgets/donate.svg"></a>

## Screenshots
<p align="center"> <img width="720" src="https://i.imgur.com/6AfXO57.png"> </img></p> 
<p align="center"> <img width="720" src="https://i.imgur.com/jipjySH.png"> </img></p> 
<p align="center"> <img width="720" src="https://i.imgur.com/JMUW6VH.png"> </img></p> 
<p align="center"> <img width="720" src="https://i.imgur.com/a7rM4sv.png"> </img></p> 
<p align="center"> <img width="720" src="https://i.imgur.com/skXFMqE.png"> </img></p> 
<p align="center"> <img width="720" src="https://i.imgur.com/AurVw5M.png"> </img></p> 
