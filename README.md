# Parasitter
<p align="center"> <img width="150" src="app/static/img/logo.png"> </img></p> 
<p align="center"> Twitter via RSS with privacy </p>
<br>
Parasitter allows you to follow your favourite twitters without Twitter even knowing it. Rssitter uses [Nitter's](nitter.net) rss feed in order to gather the latest tweets from your favourite accounts and builds a *twitter-like* feed so you can read them. We will never connect you to Twitter so your privacy is safe when using Parasitter.

### Self hosting
1. Install `python3`, `pip` and `virtualenv`.
2. Prepare a virtual environment:
    - `python3 -m venv venv`
    - `source venv/bin/activate`
  > Now you are inside of the virtual environment for python.
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
