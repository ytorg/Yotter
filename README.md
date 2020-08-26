# Parasitter
<p align="center"> <img width="150" src="app/static/img/logo.png"> </img></p> 
<p align="center"> Twitter and Youtube via RSS with privacy </p>
<br>

#### **IMPORTANT** If you want to try out the latest features you should look at [**this branch**](https://github.com/pluja/Parasitter/tree/dev-indep). Master branch is currently inactive!

## BREAKING DEPENDENCE WITH INVIDIOUS
A [**new branch**](https://github.com/pluja/Parasitter/tree/dev-indep) is being developed where I've broke dependence on Invidious.

Progress:
- [x] Video data.
- [x] Video playing
- [x] Proxy video - no Google/Youtube connections on client. [2020.08.16]
- [ ] Offer alternative to Youtube RSS.
- [ ] Search

# What is Parasitter?
Parasitter allows you to follow your favorite Twitter and YouTube accounts with full privacy. Parasitter (first version, this is [now being changed](https://github.com/pluja/Parasitter/blob/dev-indep/README.md)!) uses [Nitter's](https://nitter.net/) and [Invidious](invidio.us) rss feeds in order to gather the latest content from your favourite accounts and builds a *beautiful* feed. We will never connect you to Twitter or YouTube in any way, so your privacy is safe when using Parasitter. Parasitter is written in Python and Flask and uses Semantic-UI as its CSS framework.

Parasitter doesn't try to compete with Nitter nor Invidious. It serves as a complement, as it beneficiates from them. Parasitter is not a Twitter viewer as Nitter is or a YouTube frontend as Invidious. Instead Parasitter gathers all your accounts in one place so you can stay tuned with their latest content. 

Parasitter is possible thanks to several open-source projects that are listed on the [Powered by](#powered-by) section. Make sure to check out those awesome projects!

## Index:
* [Features](#features)
* [Security](#security)
* [Privacy](#privacy)
* [Self hosting](#self-hosting)
    * [Local](#local)
    * [Update](#updating-to-new-versions)
    * [Server](#server)
* [Powered by](#powered-by)
* [Donate](#donate-) (Please read!)

## Features:
* No JavaScript.
* 0 connections to Twitter or Youtube.
* Uses RSS feeds (could be expanded to more social networks)
* Follow Twitter accounts.
* Follow Youtube accounts.
* Watch Youtube videos.
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
Parasitter cares about your privacy, and for this it will never make any connection to Twitter or Youtube. We make use of rss feeds to fetch all the tweets and videos from your followed accounts. If you want to use a specific Nitter or Invidious instance you can replace it at the top of the file `app/routes.py`.

It is always recommended to set up a self-hosted instance. It is quite easy and conveninent and will give you full control over your data. The only data that is stored on the Database is:
* Hash of the password
* Username
* Email (Will be deprecated soon!)
* List of followed users
* List of saved posts

# Self hosting

### Local
You don't need a server to run Parasitter. You can run it on your computer locally and own your (little) data. The installation process is done on a GNU/Linux environment, but should be pretty similar on other platforms.

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

### Server
Another option is to host a Parasitter server so you can access it from anywhere or give access to your beloved friends/community. Installation is a little bit more complex than the [local](#local), but should be easy if you follow the steps.

> WARNING: This section is under construction.
##### Installing the app:
1. Install base dependencies:
   - `sudo apt-get -y update`
   - `sudo apt-get -y install python3 python3-venv python3-dev`
   - `sudo apt-get -y install mysql-server postfix supervisor nginx git`
   > Installation of MySQL will require you to enter a *database root* password.
2. Install the application:
   - `git clone https://github.com/pluja/Parasitter.git`
   - `cd Parasitter`
3. Prepare the environment:
   - `python3 -m venv venv`
   - `source venv/bin/activate`
   - (venv) $ `pip install -r requirements.txt`
4. Install deployment packages:
   - (venv) `pip install gunicorn pymysql`
5. Edit the *.env* SECRET_KEY:
   - `nano .env`
   > This will open an editor. Make sure to change the SECRET_KEY to a string of your like. Make it random and long enough.
6. Set up FLASK_APP environment variable:
   - `echo "export FLASK_APP=parasitter.py" >> ~/.profile`

##### Database configuration:
1. Enter the MySQL command prompt:
   - `mysql -u root -p`
   > It will prompt for the "root" password. This password is the one you set on the MySQL installation.
2. Create the database:
   - mysql> `create database parasitter character set utf8 collate utf8_bin;`
   - mysql> `create user 'parasitter'@'localhost' identified by '<db-password>';`
   > Replace `<db-password>` as the password for the database *parasitter* user. This one needs to match the password set on the DATABASE_URL in the *.env* file (See Step 5 of [App installation](installing-the-app))
   - mysql> `grant all privileges on parasitter.* to 'parasitter'@'localhost';`
   - mysql> `flush privileges;`
   - mysql> `quit;`
3. Upgrade the database:
   - (venv) `flask db upgrade`

#### TO BE CONTINUED!

### Powered by:
* [Nitter](https://nitter.net)
* [Invidious](https://invidio.us)
* [Flask](https://flask.palletsprojects.com/)
* [SQLAlchemy](https://docs.sqlalchemy.org/en/13/)
* [Semantic-UI](https://semantic-ui.com)
* [requests-futures](https://github.com/ross/requests-futures)
* [microblog](https://github.com/miguelgrinberg/microblog)

### Donate 💌
Testing with a public instance will soon be needed, and I will need to set up a server for this. If I want that Parasitter to go public and host some users I will need a (relativelly) good server and this is somehow expensive for me. So any contribution will be really welcome!

This project is completelly Open Source and is built on my own free time as a hobby. So if you like it, you can buy me a coffee!

- **Bitcoin**: `3EjaWjtsHz4WpbVL5Wx8Xg6MfyRRnKYj4e`
- **Monero**: `83hinYmUkMH2ANgdhxRupmakzLwN26ddePrLQvZv4E3Q1CWjq7MDzsKRcPqLPQwTvG3DdujyaxbKbMsf9VKVAmphMhsfndc`
