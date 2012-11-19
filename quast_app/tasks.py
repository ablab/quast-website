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

    from_email = 'notification@quast.bioinf.spbau.ru'
    my_email = 'vladsaveliev@me.com'
    if quast_session.user_session.email:
        user_email = quast_session.user_session.email
    else:
        user_email = None

    try:
        result = quast.main(args[1:])

        if quast_session.comment:
            subject = 'QUAST report (%s)' % quast_session.comment[:200]
        else:
            subject = 'QUAST report (data set: %s)' % quast_session.dataset.name

        send_mail(
            subject = subject,
            message = '''
            http://quast.boinf.spbau.ru/%s

            data set: %s

            %s
            ''' % (link, quast_session.dataset.name, quast_session.comment),

            from_email = from_email,
            recipient_list = [my_email, user_email],
            fail_silently = True
        )
    except Exception as e:
        if quast_session.comment:
            subject = 'QUAST failed (%s)' % quast_session.comment[:200]
        else:
            subject = 'QUAST failed (data set: %s)' % quast_session.dataset.name


        send_mail(
            subject = subject,
            message = '''
            http://quast.boinf.spbau.ru/%s

            data set: %s

            %s

            QUAST failed:
            %s.msg
            ''' % (link, quast_session.dataset.name, quast_session.comment, str(e)),

            from_email = from_email,
            recipient_list = [my_email],
            fail_silently = True
        )

        send_mail(
            subject = subject,
            message = '''
            http://quast.boinf.spbau.ru/%s

            data set: %s

            %s
            ''' % (link, quast_session.dataset.name, quast_session.comment),

            from_email = from_email,
            recipient_list = [user_email],
            fail_silently = True
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