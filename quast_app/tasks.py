from shutil import copytree
import shutil
import sys
import os
from celery.task import task
from django.conf import settings
from django.core.mail import send_mail


@task()
def start_quast((args, quast_session)):
    link = os.path.join(settings.REPORT_LINK_BASE, quast_session.report_id)

    from_email = 'notification@quast.bioinf.spbau.ru'
    def send_result_mail(email, add_to_end='', fail=False):
        if email == '':
            return

        if fail:
            subject = 'QUAST failed'
        else:
            subject = 'QUAST report'

        if quast_session.caption:
            subject += ' (%s)' % quast_session.caption
        else:
            subject += ' (data set: %s)' % quast_session.dataset.name

        send_mail(
            subject = subject,
            message = '''
                http://quast.bioinf.spbau.ru%s

                Data set: %s

                %s
                %s

                %s
                ''' % (link,
                       quast_session.dataset.name,
                       quast_session.caption,
                       quast_session.comment,
                       add_to_end),

            from_email = from_email,
            recipient_list = [email],
            fail_silently = True
        )

    my_email = 'vladsaveliev@me.com'
    if quast_session.user_session.email:
        user_email = quast_session.user_session.email
    else:
        user_email = None

    try:
        if not settings.QUAST_DIRPATH in sys.path:
            sys.path.insert(1, settings.QUAST_DIRPATH)
        import quast

        quast.qconfig.html_report = False
        quast.qconfig.draw_plots = False

        result = quast.main(args[1:])

        send_result_mail(my_email)
        send_result_mail(user_email)

    except Exception as e:
        send_result_mail(my_email, add_to_end=str(e), fail=True)
        send_result_mail(user_email, fail=True)
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