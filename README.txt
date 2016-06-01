***************************************************
FIRST INSTALLATION
***************************************************
Pre-intallations
Ubuntu:
    $ sudo apt-get install sqlite3
    $ sudo apt-get install python-dev
    $ sudo apt-get install libevent-dev
    # sudo apt-get install MySQL-python

Mac OS:
    $ brew install sqlite3
    $ brew install libevent
    $ export CFLAGS=-I/brew/include

$ mkdir quast
$ cd quast

Clone command line quast application:
    $ git clone --recursive https://github.com/ablab/quast-website.git
    $ mv quast-website source

Install python virtual environment:
    $ easy_install pip
    $ pip install virtualenv
    $ virtualenv virtualenv
    $ source virtualenv/bin/activate
    $ pip install -r source/pip_requirements.txt  # Installs dependencies listed in the file. In my case, for sqlalchemy sudo was reqiured, so if something is not working, try 'sudo pip install sqlalchemy'

Initialize database:
$ source/manage.py migrate

Start celery that will process tasks
$ source/manage.py celeryd

(if running locally) start Django test webserver:
    export DEVELOPMENT=1
    $ source/manage.py runserver localhost:8000

(if on a web server) configure Apache:
    Create an Apache configuration file in /etc/apache2/sites-available/quast containg the folling. Please replace ServerName and paths starting with '/var/www/quast' according to your environment)

        <VirtualHost *:80>
            ServerAdmin webmaster@localhost
            ServerName quast.bioinf.spbau.ru
            DocumentRoot /var/www/quast/source

            <Directory /var/www/quast/source>
                    Options FollowSymLinks MultiViews
                   AllowOverride None
                    Order allow,deny
                    allow from all
            </Directory>

            ErrorLog ${APACHE_LOG_DIR}/quast-error.log

            # Possible values include: debug, info, notice, warn, error, crit,
            # alert, emerg.
            LogLevel warn

            CustomLog ${APACHE_LOG_DIR}/quast-access.log combined

            Alias /static/ /var/www/quast/source/static/

            <Directory /var/www/quast/source/static>
                    Order deny,allow
                    Allow from all
            </Directory>

            WSGIDaemonProcess quast user=saveliev group=www-data python-path=/var/www/quast/virtualenv/lib/python2.7/site-packages
            WSGIProcessGroup quast
            WSGIScriptAlias / /var/www/quast/source/wsgi.py

            <Directory /var/www/quast/source>
                    <Files wsgi.py>
                            Order deny,allow
                            Allow from all
                    </Files>
            </Directory>
        </VirtualHost>

    Start apache
    $ sudo apachectl start


***************************************************
DEPLOYING CHANGES
***************************************************
$ cd source

Locally push everything to Github:
    $ git all
    $ git commit -m '[comment]'
    $ git up
    $ git push

On the server, pull changes:
    $ git pull
Collect static files:
    # source/manage.py collectstatic
Gracefully restart Apache:
    $ sudo apachectl graceful

If you want to pull latest changes for the command-line Quast,
    $ cd quast
    $ git pull
    $ cd ..
    $ cd git all
    $ cd commit -m 'Updated command-line Quast'
    $ cd push
On the server:
    $ git pull
    $ source/manage.py collectstatic
    Interrupt celery and start again:
    $ source/manage.py celeryd
    $ sudo apachectl graceful

Note that data and virtualenv directories are kept different for development and deployment.
