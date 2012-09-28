***************************************************
FIRST INSTALLATION
Ubuntu:
    sudo apt-get install sqlite3
    sudo apt-get install python-dev
    sudo apt-get install libevent-dev

Mac OS:
    brew install sqlite3
    brew install libevent
    export CFLAGS=-I/brew/include

Both:
    git clone https://github.com/ablab/quast-website.git
    cd quast
    easy_install pip
    pip install virtualenv
    virtualenv virtualenv
    source virtualenv/bin/activate
    cd quast-website
    pip install -r pip_requirements.txt

***************************************************
DEPLOYING CHANGES
cd quast/quast-website

Locally push everything to Github:
    git all
    git commit -m '[comment]'
    git up
    git push

On Morality, pull changes:
    git pull
Gracefully restart Apache:
    sudo apachectl graceful

Data and virtualenv directories are kept different for development and deployment.