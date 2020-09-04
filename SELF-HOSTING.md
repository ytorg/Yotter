<h1> UNDER CONSTRUCTION </h1>
<a href="https://github.com/pluja/Yotter/tree/master"><img alt="Installation Working" src="https://img.shields.io/badge/Working-2020.09.04-green.svg"></img></a>
<br>
<a href="https://github.com/pluja/Yotter/tree/master"><img alt="Tested on Ubuntu" src="https://img.shields.io/badge/Tested On-Ubuntu 20.04LTS-blue.svg"></img></a>

#### Step 1: Base setup
1. Connect to your server via SSH or direct access.
    * (Recommended) Set up password-less login with ssh-keys.

2. Install base dependencies:
* `sudo apt-get -y update`

* `sudo apt-get -y install python3 python3-venv python3-dev`

* `sudo apt-get -y install mysql-server supervisor nginx git make`

> When installing MySQL-server it will prompt for a root password. Set up a password of your like, this will be the MySQL databases master password and will be required later, so don't forget it!

3. Clone this repository and acccess folder:
* `git clone https://github.com/pluja/Yotter`

* `cd Yotter`

4. Create a Python virtual environment and populate it with dependencies:
* `python3 -m venv venv`
* `source venv/bin/activate`

* `pip install -r requirements.txt`

> You can edit the `yotter-config` file

5. Install gunicorn (production web server for Python apps) and pymysql:
`pip install gunicorn pymysql`

6. Set up `.env`
    1. (PRE) Generate a random string and copy it to clipboard:
        `python3 -c "import uuid; print(uuid.uuid4().hex)"`

    2. Create a `.env` file on the root folder of the project (`/home/ubuntu/Yotter/.env`):
        ```
        SECRET_KEY=<RandomStringHere!>
        DATABASE_URL=mysql+pymysql://yotter:<db-password>@localhost:3306/yotter
        ```

#### Step 2: Setting up the MySQL Database:
* Open the MySQL prompt line (Use the previously set MySQL root password!)
    `mysql -u root -p`

Now you should be on the MySQL prompt line (`mysql>`). So let's create the databases:

> Change `<db-password>` for a password of your like. It will be the password for the dabase user `yotter`. Don't choose the same password as the root user of MySQL for security.

> The password for the **yotter** user needs to match the password that you included in the `DATABASE_URL` variable in the `.env` file. If you didn't change it, you can change it now.

```
mysql> create database yotter character set utf8 collate utf8_bin;
mysql> create user 'yotter'@'localhost' identified by '<db-password>';
mysql> grant all privileges on yotter.* to 'yotter'@'localhost';
mysql> flush privileges;
mysql> quit;
```

If your set up was correct, you should now be able to run:

`flask db init`
`flask db migrate`

#### Step 3: Setting up Gunicorn and Supervisor
When you run the server with flask run, you are using a web server that comes with Flask. This server is very useful during development, but it isn't a good choice to use for a production server because it wasn't built with performance and robustness in mind. Instead of the Flask development server, for this deployment I decided to use gunicorn, which is also a pure Python web server, but unlike Flask's, it is a robust production server that is used by a lot of people, while at the same time it is very easy to use. [ref](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xvii-deployment-on-linux)

* Start yotter under Gunicorn:

`gunicorn -b localhost:8000 -w 4 yotter:app`

The supervisor utility uses configuration files that tell it what programs to monitor and how to restart them when necessary. Configuration files must be stored in /etc/supervisor/conf.d. Here is a configuration file for Yotter, which I'm going to call yotter.conf [ref](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xvii-deployment-on-linux).

* Create a yotter.conf file on `/etc/supervisor/conf.d/`:

> You can run `nano /etc/supervisor/conf.d/yotter.conf` and paste the text below:

> Make sure to fit any path and user to your system.

```
[program:yotter]
command=/home/ubuntu/yotter/venv/bin/gunicorn -b localhost:8000 -w 4 yotter:app
directory=/home/ubuntu/yotter
user=ubuntu
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
```

After you write this configuration file, you have to reload the supervisor service for it to be imported:
`sudo supervisorctl reload`

#### Step 4: Set up Nginx
The Yotter application server powered by gunicorn is now running privately port 8000. Now we need to expose the application to the outside world by enabling public facing web server on ports 80 and 443, the two ports too need to be opened on the firewall to handle the web traffic of the application. I want this to be a secure deployment, so I'm going to configure port 80 to forward all traffic to port 443, which is going to be encrypted. [ref](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xvii-deployment-on-linux).

* `sudo rm /etc/nginx/sites-enabled/default`

Create a new Nginx site, you can run `sudo nano /etc/nginx/sites-enabled/yotter`

And write this on it:
```
server {
    server_name  <yourdomain>;

    location / {
        proxy_pass http://localhost:8000;
    }
}
```

[Follow this instructions to install certbot and generate an ssl certificate](https://certbot.eff.org/lets-encrypt/ubuntufocal-nginx)
