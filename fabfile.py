def git_up():
    run("git up")

def git_st():
    run("git st")

def reboot():
    sudo("apachectl graceful")