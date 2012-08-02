import runpy
import subprocess
from celery import task
from celery.app.base import Celery
import os

quast_path = os.path.abspath('../quast/')

celery = Celery('celery_start_quast', broker='redis://localhost:6379/0')

@task()
def start_quast(args):
    out = ''
    err = ''
    try:
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while True:
            line = proc.stderr.readline()
            if line != '':
                out = out + 'Quast err ' + line + '\n'
            else:
                break
        proc.wait()

        return out + err

    except Exception as e:
        raise Exception(out + err + '\n' + e.strerror)


