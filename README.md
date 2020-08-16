# Parasitter
<p align="center"> <img width="150" src="app/static/img/logo.png"> </img></p> 
<p align="center"> Twitter and Youtube via RSS with privacy </p>
<br>

### This is a new version where I'm trying to break dependance with Invidious (and later Nitter). ~~Currently the video playing page (`/video/<video-id>`) no longer depends on Invidious, but it connects to *googlevideo*~~. Google free video streams are now working! Yay!

Parasitter allows you to follow your favorite Twitter and YouTube accounts with full privacy using rss feeds in order to gather the latest content from your favourite accounts and builds a *beautiful* feed so you can read them. Parasitter is written in Python and Flask and uses Semantic-UI as its CSS framework.

Parasitter is possible thanks to several open-source projects that are listed on the [Powered by](#powered-by) section. Make sure to check out those awesome projects!

## Index:
* [Features](#features)
* [Security](#security)
* [Privacy](#privacy)
* [Self hosting](#self-hosting)
    * [Test it!](#test)
    * [Update](#updating-to-new-versions)
* [Powered by](#powered-by)
* [Donate](#donate-)

## Features:
* No JavaScript.
* Uses RSS feeds (could be expanded to more social networks)
* Follow Twitter accounts.
* Follow Youtube accounts.
* Save your favourite Tweets.
* Save your favourite Youtube videos [Coming soon!]
* Tor-friendly.
* Terminal-friendly.
* Easy 1 minute self-hosting deploy.
* No need for domain, runs locally.
> And many more to come!

## Security
Only the hash of your password is stored on the database. Also no personal information of any kind is kept on the app itself, if a hacker gets access to it only thing they could do would be to follow/unfollow some accounts.

I always recommend self-hosting, as you will be the only person with access to the data.

## Privacy
Parasitter cares about your privacy, and for this it will never make any connection to Twitter or Youtube. We make use pf rss feeds to fetch all the tweets from your followed accounts. If you want to use a specific Nitter or Invidious instance you can replace it on the file `app/routes.py`.

* Hash of the password
* Username
* Email (we won't send you any mails so you can make up the mail) - This is for future versions.
* List of followed users
* List of saved posts

# Self hosting

### Test
You can test this new version.
> IMPORTANT: Connections to googlevideo will be made to stream the videos. It is recommended to use a VPS server to preserve your privacy.

1. Install `python3`, `pip3`, `python3-venv` (optional) and `git`.
2. Clone this repository:
    - `git clone https://github.com/pluja/Parasitter.git`
3. Navigate to the project folder:
    - `cd Parasitter`
4. [Optional] Prepare a virtual environment and activate it:

   > Python lets you create virtual environments. This allows you to avoid installing all the `pip` packages on your system.   
   If you don't mind about that, you can jump to step **5.** and ignore everything about "[env]".
    - `python3 -m venv venv`
    - `source venv/bin/activate`
    > Now you are inside of the virtual environment for python. All instructions wiht [env] indicate that must be done inside the env if you decided to create one. From now on, you will always need to start the application from within the virtual env.
5. [env] Update pip
    - `pip3 install --upgrade pip`
6. [env] Install the required libraries:
    - `pip3 install -r requirements.txt`
       > Use `sudo` or, preferably `--user`, if not working.
7. [env] Initialize and prepare the database.
    - `flask db init`
    - `flask db migrate`
    - `flask db upgrade`
8. [env] Run the application.
    - `flask run`
9. Go to "http://localhost:5000/" and enjoy.

### Updating to new versions:
**NOTE: Updating will never delete your database, your following list will not be erased.**
1. Navigate to the git repository (the one you cloned when installing).
2. Pull new changes:
    - `git pull`
4. Install new packages (if any):
   - `pip install -r requirements.txt`
   > It may be that there are no new packages to install. In that case, all requirements will be satisfied.

5. [opt] This next step is only needed if you are running a version previous to [2020-07-15](CHANGELOG.md). Then you will need to update the database:
    - `flask db migrate`
    - `flask db upgrade`
6. Done! You are on latest version.
> **See [CHANGELOG](CHANGELOG.md) for a list of changes.**

### Powered by:
* [RSSBridge](https://github.com/RSS-Bridge/rss-bridge)
* [youtube-dl](https://github.com/ytdl-org/youtube-dl)
* [Flask](https://flask.palletsprojects.com/)
* [SQLAlchemy](https://docs.sqlalchemy.org/en/13/)
* [Semantic-UI](https://semantic-ui.com)
* [requests-futures](https://github.com/ross/requests-futures)
* [microblog](https://github.com/miguelgrinberg/microblog)

### Donate 💌
This project is completelly Open Source and is built on my own free time as a hobby. I am (almost) alone with it [one contributor helped me with a small thing but he's not an active contributor anymore].

If you like it, you can buy me a coffee!

- **Bitcoin**: `3EjaWjtsHz4WpbVL5Wx8Xg6MfyRRnKYj4e`
- **Monero**: `83hinYmUkMH2ANgdhxRupmakzLwN26ddePrLQvZv4E3Q1CWjq7MDzsKRcPqLPQwTvG3DdujyaxbKbMsf9VKVAmphMhsfndc`
