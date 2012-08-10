import sys
import os
from celery.task import task
from quast_website import settings

quast_path = settings.quast_dirpath

@task()
def start_quast(args):
    if not quast_path in sys.path:
        sys.path.insert(1, quast_path)

    import quast
    print 'Running Quast'
    return quast.main(args[1:])


#   out = ''
#   err = ''
#   try:
#       proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#       while True:
#           line = proc.stderr.readline()
#           if line != '':
#               out = out + 'Quast err ' + line + '\n'
#           else:
#               break
#       proc.wait()
#
#   except Exception as e:
#       raise Exception(out + err + '\n' + e.strerror)