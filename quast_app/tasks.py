from shutil import copytree
import shutil
import sys
import os
from celery.task import task
from django.conf import settings
from django.core.mail import send_mail

@task()
def start_quast((args, quast_session)):
    if not settings.QUAST_DIRPATH in sys.path:
        sys.path.insert(1, settings.QUAST_DIRPATH)
    import quast

    quast.qconfig.html_report = False
    quast.qconfig.draw_plots = False

    link = os.path.join(settings.REPORT_LINK_BASE, quast_session.report_id)
    emails = ['vladsaveliev@me.com']
    if quast_session.user_session.email:
        emails.append(quast_session.user_session.email)

    try:
        result = quast.main(args[1:])

        send_mail(
            subject='QUAST report is ready (' + quast_session.dataset.name + ').',
            message='Link to your report: <a href="' + link + '">' + link + '</a>',
            from_email='notification@quast.bioinf.spbau.ru',
            recipient_list=emails,
            fail_silently=True
        )

    except Exception as e:
        send_mail(
            subject='QUAST report is ready (' + quast_session.dataset.name + ').',
            message='Link to your report: <a href="' + link + '">' + link + '</a>',
            from_email='notification@quast.bioinf.spbau.ru',
            recipient_list=['vladsaveliev@me.com'],
            fail_silently=True
        )
        raise e

    reload(quast)
    return result

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