import sys
from fabric.api import *
from fabric import network
from fabric.contrib import files
from fabric import operations, utils

env.hosts = ['saveliev@192.168.222.254', 'saveliev@194.85.238.21']
set(fab_user='alex',
    fab_hosts=['clientsite.com'],
    root='/home/alex/websites/',
    site='clientsite')

def reboot():
    sudo("apachectl graceful")

def test():
    local("../virtualenv/bin/python manage.py test quast_app")

def st():
    local("git st")

def all():
    local("git all")

def commit(comment):
    with settings(warn_only=True):
        return local("git commit -m '%s'" % comment)

def add_commit(comment):
    all()
    return commit(comment)

def up():
    local("git up")

def push():
    local("git push")

def upush():
    up()
    push()

def git(comment):
    res = add_commit(comment)
    upush()



def restart_celeryd():
    sudo("/etc/init.d/celeryd restart")



def manage(command):
    run('/var/www/quast/virtualenv/bin/python manage.py ' + command)

def syncdb(params=''):
    manage('syncdb --noinput %s' % params)


code_dir = '/var/www/quast/quast-website'

def refresh():
    with cd(code_dir):
        run("git up")

def deploy(comment):
    git(comment)
    refresh()







