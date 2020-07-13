# Parasitter
<p align="center"> <img width="150" src="app/static/img/logo.png"> </img></p> 
<p align="center"> Twitter via RSS with privacy </p>
<br>
Parasitter allows you to follow your favourite twitters without Twitter even knowing it. Rssitter uses [Nitter's](nitter.net) rss feed in order to gather the latest tweets from your favourite accounts and builds a *twitter-like* feed so you can read them. We will never connect you to Twitter so your privacy is safe when using Parasitter.


Parasitter is written with Python and Flask and uses Semantic-UI as its CSS framework.


## Security
Only the hash of your password is stored on the database. Also no personal information of any kind is kept on the app itself, if a hacker gets access to it only thing they could do would be to follow/unfollow some accounts.

I always recommend self-hosting, as you will be the only person with access to the data.

## Self hosting (2 min set-up)
1. Install `python3`, `pip3` and `git`.
2. Clone this repository:
    - `git clone https://github.com/pluja/Parasitter.git`
3. Navigate to the project folder:
    - `cd Parasitter`
4. Prepare a virtual environment and activate it:
    - `python3 -m venv venv`
    - `source venv/bin/activate`
    > Now you are inside of the virtual environment for python. All instructions wiht [env] indicate that must be done inside the env.
3. [env] Update pip
    - `pip install --upgrade pip`
4. [env] Install the dependencies:
    - `pip3 install flask flask-sqlalchemy flask-migrate python-dotenv flask-wtf flask-login email-validator feedparser`
        > It may require you to use *sudo*
5. [env] Initialize and prepare the database.
    - `flask db init`
    - `flask db migrate`
    - `flask db upgrade`
6. [env] Run the application.
    - `flask run`
7. Go to "http://localhost:5000/" and enjoy.


### Powered by:
* [Nitter](https://nitter.net)
* [Flask](https://flask.palletsprojects.com/)
* [SQLAlchemy](https://docs.sqlalchemy.org/en/13/)
* [Semantic-UI](https://semantic-ui.com)
