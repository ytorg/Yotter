<p align="center"> <img width="700" src="app/static/img/banner.png"> </img></p> 
<p align="center">
   <a href="https://www.gnu.org/licenses/gpl-3.0"><img alt="License: GPL v3" src="https://img.shields.io/badge/License-GPLv3-blue.svg"></img></a>
   <a href="https://github.com/pluja/Yotter"><img alt="Development state" src="https://img.shields.io/badge/State-Beta-blue.svg"></img></a>
   <a href="https://github.com/pluja/Yotter/pulls"><img alt="Pull Requests Welcome" src="https://img.shields.io/badge/PRs-Welcome-green.svg"></img></a>
   <a href="https://github.com/pluja/Yotter/tree/master"><img alt="Formerly named Parasitter" src="https://img.shields.io/badge/Formerly-Parasitter-blue.svg"></img></a>
</p> 


Yotter allows you to follow and gather all the content from your favorite Twitter and YouTube accounts in a *beautiful* feed so you can stay up to date without compromising your privacy at all. Yotter is written with Python and Flask and uses Semantic-UI as its CSS framework.

Yotter is possible thanks to several open-source projects that are listed on the [Powered by](#powered-by) section. Make sure to check out those awesome projects!

## Index:
* [Why](#why)
* [Features](#features)
* [Screenshots](#screenshots)
* [Privacy and Security](#-privacy)
* [Self hosting](#-self-hosting)
    * Install & Test
        * [Normal installation](#-test)
        * [Docker installation](#using-docker)
    * [Hosting on a server](#-hosting-on-a-server)
    * [Update](#-updating-to-newer-versions)
    * [Configure server](#configure-the-server)
* [Powered by](#-powered-by)
* [Donate](#-donate)

## Why
At first I started working on this project as a solution for following Twitter accounts (a thing that can't be done with Nitter) and getting a Twitter-like feed. Weeks later the leader of Invidious, Omar Roth, announced that he was stepping away from the project. As an Invidious active user, this made me think that a new alternative was needed for the community and also an alternative with an easier language for most people (as Invidious is written in Crystal). So I started developing a 'written-in-python Invidious alternative' and it went quite well.

I hope that this project can prosperate, gain contributors, new instances and create a good community around it.

## Features:
- [x] No Ads.
- [x] No JavaScript.
- [x] Minimalist.
- [x] Search on Twitter and Youtube.
- [x] Zero connections to Google/Twitter on the client.
- [x] Follow Twitter accounts.
- [x] Follow Youtube accounts.
- [x] Save your favourite Tweets.
- [x] Tor-friendly.
- [x] Terminal-browser friendly.

> And many more to come!

## 🎭 Privacy
#### 🌐 Connections
Yotter cares about your privacy, and for this it will never make any connection to Twitter or Youtube on the client. Every request is proxied through the Yotter server; video streaming, photos, data gathering, scrapping, etc.

The Yotter server connects to Google (Youtube) and Nitter in order to gather all the necessary data. Then it serves it (proxyed through itself) to the client. This means that as a client, you will never connect to Google - the Yotter server will do it for you. So if you want to set up a Yotter server for privacy reasons I recommend you to set it up on a remote VPS so you don't share your IP with Google or use a VPN on the server. 

If you don't mind exposing your IP making requests to Google then you can set it up wherever you want. Even with this method you will **avoid all trackers, ads, heavy-loaded pages, etc**. - Even with this method, you can stay safe if you use a VPN to hide your IP.

#### 🛡️ Your data
The only things the database stores are:
* Hash of the password
* Username
* List of followed users
* List of saved posts
* Some user configurations (Dark theme, etc)

This data will never be used for any other purpose than offering the service to the user. It's not sent anywhere, never.

#### 🔐 Security
Only the hash of your password is stored on the database. Also, no personal information of any kind is required nor kept, if a hacker gets access to the database the only thing they could do would be to follow/unfollow some accounts. So there's no motivation in 'hacking' Yotter.

I always recommend self-hosting, as you will be the only person with access to the data.

> Important note: The **client** never connects to Google / Youtube however, the server does in order to gather all the necessary things!

#### Others
If you want to use a specific Nitter instance you can replace it on the file `app/routes.py`.

## 🏠 Self hosting

### 🐣 Test
You can test this new version.

##### IMPORTANT: Connections to googlevideo will be made to stream the videos. It is recommended to use a VPS server or a VPN to preserve your privacy. This version is intended for a remote server.

1. Install `python3`, `pip3`, `python3-venv` (optional) and `git`.

2. Clone this repository:
    - `git clone https://github.com/pluja/Yotter.git`
    
3. Navigate to the project folder:
    - `cd Yotter`
   
4. Prepare a virtual environment and activate it:
   > Python lets you create virtual environments. This allows you to avoid installing all the `pip` packages on your system.
    - `python3 -m venv venv`
    - `source venv/bin/activate`
    > Now you are inside of the virtual environment for python. All instructions wiht [env] indicate that must be done inside the env if you decided to create one. From now on, you will always need to start the application from within the virtual env.
    
5. [env] Update pip
    - `python3 pip install --upgrade pip`
    
6. [env] Install the required libraries:
    - `python3 pip install -r requirements.txt`
       > If you get errors, try running `source venv/bin/activate` again of use `--user` option.
       
7. [env] Initialize and prepare the database.
    - `flask db init`
    - `flask db migrate`
    - `flask db upgrade`
    > If you get *`"No such command db"`*, try running `source venv/bin/activate` again.
    
8. [env] Run the application.
    - `flask run`
    > You can optionally use `flask run --host 0.0.0.0` so you can use Yotter from other devices from the same network using the host device's IP address and port. ¡Test it from a smartphone!
    
9. Go to "http://localhost:5000/" and enjoy.

### 🐋 Using Docker:
A quick deployment

1. Install Docker:
    - `https://docs.docker.com/engine/install/`

2. Clone this repository:
    - `git clone https://github.com/pluja/Yotter.git`
    
3. Navigate to the project folder:
    - `cd Yotter`

4. Build the docker image:
    - `docker build -t yotter .`

5. Run the container:
    - `docker run -p 5000:5000 yotter`
    
6. Go to "http://localhost:5000/" and enjoy.

### 🔗 Hosting on a server:
`SOON`

### 🐓 Updating to newer versions:
**IMPORTANT: Before updating to newer versions, always export your data on `Settings>Export Data`. A major version update could have changes on the whole database and you may be forced to remove and reset the database (only when running locally)!**

1. Navigate to the git repository (the one you cloned when installing).

2. Pull new changes:
    - `git pull`
    
4. Install new packages (if any):
   - `pip install -r requirements.txt`
   > It may be that there are no new packages to install. In that case, all requirements will be satisfied.

5. Update the database:
    - `flask db migrate`
    - `flask db upgrade`
> If you experience any error in this step, it might be that there were big changes on the database structure. You can solve it by exporting your data, then deleting and resetting the database. Run `rm -rf app.db migrations` and then `flask db init`. Then run step 5 normally.

6. Done! You are on latest version.
> **See [CHANGELOG](CHANGELOG.md) for a list of changes.**

### ⚙️ Configure the server
You will find in the root folder of the project a file named `yotter-config.json`. This is the global config file for the Yotter server.

Currently available config is:
* **nitterInstance**: Nitter instance that will be used when fetching Twitter content.
* **maxInstanceUsers**: Max users on the instance. When set to `0` it closes registrations.

## ⛽ Powered by:
* [Nitter](https://nitter.net/)
* [youtube-dl](https://github.com/ytdl-org/youtube-dl)
* [Flask](https://flask.palletsprojects.com/)
* [SQLAlchemy](https://docs.sqlalchemy.org/en/13/)
* [Semantic-UI](https://semantic-ui.com)
* [requests-futures](https://github.com/ross/requests-futures)
* [microblog](https://github.com/miguelgrinberg/microblog)
* [Video.js](https://videojs.com/)
* [My fork of youtube_search](https://github.com/pluja/youtube_search-fork)

## 💌 Donate
This project is completely free and Open Source and will always be.

Funding will be used 100% for opening and mantaining an online public instance of Yotter, this will be hosted on Netcup and will (at first) be the *VPS 500 G8*. I mention all of this in case you want to check the prices.
#### Crypto (preferred):
- **Bitcoin**: `3EjaWjtsHz4WpbVL5Wx8Xg6MfyRRnKYj4e`
- **Monero**: `83hinYmUkMH2ANgdhxRupmakzLwN26ddePrLQvZv4E3Q1CWjq7MDzsKRcPqLPQwTvG3DdujyaxbKbMsf9VKVAmphMhsfndc`
#### Fiat:
- <a href="https://liberapay.com/pluja/donate"><img alt="Donate using Liberapay" src="https://liberapay.com/assets/widgets/donate.svg"></a>

## 🖼️ Screenshots
<p align="center"> <img width="720" src="https://i.imgur.com/6AfXO57.png"> </img></p> 
<p align="center"> <img width="720" src="https://i.imgur.com/jipjySH.png"> </img></p> 
<p align="center"> <img width="720" src="https://i.imgur.com/JMUW6VH.png"> </img></p> 
<p align="center"> <img width="720" src="https://i.imgur.com/a7rM4sv.png"> </img></p> 
<p align="center"> <img width="720" src="https://i.imgur.com/skXFMqE.png"> </img></p> 
<p align="center"> <img width="720" src="https://i.imgur.com/AurVw5M.png"> </img></p> 
