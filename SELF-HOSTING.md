<a href="https://github.com/pluja/Yotter"><img alt="Installation Working" src="https://img.shields.io/badge/Status-Working 2020.09.05-green.svg"></img></a>
<a href="https://github.com/pluja/Yotter"><img alt="Tested on Ubuntu" src="https://img.shields.io/badge/Tested On-Ubuntu Server 20.04LTS-blue.svg"></img></a>

# Why should I self host?
Self-hosting gives you the whole power over the service and the data. You can set up a server for your own personal use or share it with friends and family. Or, why not go further and share it with the whole world?

When you self-host you make internet stronger and more censorship resistant. If one Yotter instance goes down for any reason, there will be all other instances online and ready to host new users.

## Pre-Installation

You will need a server of your own, or you can rent a VPS server on any service you like. Minimum requirements for about 20 users are 2GB of RAM and a Linux Server. It is better if the server is dedicated as whole to Yotter as it will improve performance and security.

First of all, you will need to set up a new user on the server. For security reasons you should never use a `root` user to set up a service. If you already have a non-root user you can use that one and skip the following steps.

We will create a user named `ubuntu` as I will be setting this up on an ubuntu machine. So, if you choose a different username make sure you replace it on future commands. We will create and login to the user as follows:

```
# adduser --gecos "" ubuntu
# usermod -aG sudo ubuntu
# su ubuntu
$ cd
```

If you now type `pwd` and hit enter, you shuould see that the current path is `/home/<user>/`

Now you should be logged in. Make sure to set up a good password. It is recommended to use ssh keys to log-in remotelly and disable the password login on all users.

### Step 1: Base setup
1. Connect to your server via SSH or direct access.
    - `ssh ubuntu@<ipaddress>`
    - [x] (Recommended) Set up password-less login with ssh-keys.

2. Install base dependencies:
* `sudo apt-get -y update`

* `sudo apt-get -y install python3 python3-venv python3-dev`

* `sudo apt-get -y install mysql-server supervisor nginx git`

> When installing MySQL-server it will prompt for a root password. Set up a password of your like, this will be the MySQL databases master password and will be required later, so don't forget it!

If after the MySQL-server installation you have not been prompted to create a password for the `root` user, run `sudo mysql_secure_installation`

3. Clone this repository and acccess folder:
* `git clone https://github.com/pluja/Yotter`

* `cd Yotter`

4. Create a Python virtual environment and populate it with dependencies:
* `python3 -m venv venv`
* `source venv/bin/activate`

* `pip install wheel`
* `pip install cryptography`
* `pip install -r requirements.txt`

> You can edit the `yotter-config.json` file

5. Install gunicorn (production web server for Python apps) and pymysql:
`pip install gunicorn pymysql`

6. Set up the database tables:
* `flask db init`
* `flask db migrate`
* `flask db upgrade`

7. Set up `.env`
    1. (PRE) Generate a **random string** and copy it to clipboard:
        `python3 -c "import uuid; print(uuid.uuid4().hex)"`

    2. Create a `.env` file on the root folder of the project (`/home/ubuntu/Yotter/.env`):
        ```
        SECRET_KEY=<RandomString>
        DATABASE_URL=mysql+pymysql://yotter:<db-password>@localhost:3306/yotter
        ```
Make sure you change `<RandomString>` and `>db-password>`. `<db-password>` should be different from the password of the database root user (the one you set up on step 1.2). This password will be needed later.

#### Step 2: Setting up the MySQL Database:
* Open the MySQL prompt line (Use the previously set MySQL root password!)
    `mysql -u root -p`

> If you have problems with the root password try running `sudo mysql` and then run this query: `ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'YOUR_PASSWORD';`. This changes the password for the user `root` by `YOUR_PASSWORD`

Now you should be on the MySQL prompt line (`mysql>`). So let's create the databases:

> Change `<db-password>` for a password of your like. It will be the password for the dabase user `yotter`. Don't choose the same password as the root user of MySQL for security.

> The password `<db-password>` for the **yotter** user needs to match the password that you included in the `DATABASE_URL` variable in the `.env` file. If you want to change it, you can change it now.

```
mysql> create database yotter character set utf8 collate utf8_bin;
mysql> create user 'yotter'@'localhost' identified by '<db-password>';
mysql> grant all privileges on yotter.* to 'yotter'@'localhost';
mysql> flush privileges;
mysql> quit;
```

If your set up was correct, you should now be able to run:

* `flask db upgrade`

#### Step 3: Setting up Gunicorn and Supervisor
When you run the server with flask run, you are using a web server that comes with Flask. This server is very useful during development, but it isn't a good choice to use for a production server because it wasn't built with performance and robustness in mind. Instead of the Flask development server, for this deployment I decided to use gunicorn, which is also a pure Python web server, but unlike Flask's, it is a robust production server that is used by a lot of people, while at the same time it is very easy to use. [ref](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xvii-deployment-on-linux)

* Start yotter under Gunicorn and check it has no errors:

`gunicorn -b localhost:8000 -w 4 yotter:app`

Once you see that no errors appear, you can stop gunicorn by pressing `Ctrl+C`.

The supervisor utility uses configuration files that tell it what programs to monitor and how to restart them when necessary. Configuration files must be stored in /etc/supervisor/conf.d. Here is a configuration file for Yotter, which I'm going to call yotter.conf [ref](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xvii-deployment-on-linux).

* Create a yotter.conf file on `/etc/supervisor/conf.d/`:

> You can run `nano /etc/supervisor/conf.d/yotter.conf` and paste the text below:

> Make sure to fit any path and user to your system.

```
[program:yotter]
command=/home/ubuntu/Yotter/venv/bin/gunicorn -b localhost:8000 -w 4 yotter:app
directory=/home/ubuntu/Yotter
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

   location /static {
        # handle static files directly, without forwarding to the application
        alias </path/to>/Yotter/app/static;
        expires 30d;
    }
}
```
Make sure to replace `<yourdomain>` by the domain you are willing to use for your instance (i.e example.com). 

You will also need to change the `</path/to>` after `alias` to fit your system. You have to point to the Yotter folder, in this set up it would be `/home/ubuntu` as it is the location where we cloned the Yotter app. This alias is created to handle static files directly, without forwarding to the application.

Once done, you can run `sudo service nginx reload`

Now you need to install an SSL certificate on your server so you can use HTTPS:
[Follow this instructions to install certbot and generate an ssl certificate so your server can use HTTPS](https://certbot.eff.org/lets-encrypt/ubuntufocal-nginx)

> Note that you will have to create an 'A Record' on the DNS of your domain to point to the IP of your server.

## Updating the server
Updating the server should always be pretty easy. These steps need to be run on the Yotter folder and with the python virtual env activated.

```
(venv) $ git pull
(venv) $ sudo supervisorctl stop yotter
(venv) $ flask db migrate
(venv) $ flask db upgrade
(venv) $ pip install -r requirements.txt
(venv) $ sudo supervisorctl start yotter
```

## Other configurations

### Removing log-in restrictions
> (NOT TESTED -  COULD CRASH THE APP) Note that some routes make usage of the `current_user` variable to look if the current user is following some user or not, if you remove the restriction for such routes the app will crash. This will be solved on future releases.

For the example, let's allow for anyone to watch a video on our instance. Even if they aren't registered users. First we need to find the route that we want to allow, you can do it by navigating to the page and taking a look at the URL. Anything after the first `/` is the app route. When we're watching a video, the route is `/watch?v=<videoId>`.

Now on the file `routes.py` we will search for the code that the server runs when we navigate to that route. You can use the Find function on your text editor and search for `/watch`. Now, you will see that right below the definition of the route, `@app.route('/watch')`, there is a `@login_required` line. If you delete that line, no restriction will now be applied to that route.

But you must know that videos and images are proxied through the instance. So we will need to allow another route. For video streaming, the route is `/stream` and for images it is `/img`. So you just need to delete the `login_required` from those two other routes.

You can now reload the server and you will see that, without logging in, you can now watch videos.


