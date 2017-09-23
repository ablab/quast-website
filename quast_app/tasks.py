import shutil
import sys
from django.template.loader import render_to_string
import os
import traceback
from celery.task import task
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives

import logging
logger = logging.getLogger('quast')
mailer = logging.getLogger('quast_mailer')


#@task()
#def remove_all_contigs(file_names):
#    for fname in file_names:
#        file =
#
#        contigs_fpath = os.path.join(settings.INPUT_ROOT_DIRPATH,
#                                     self.user_session.input_dirname,
#                                     contigs_file.fname)
#        if os.path.isfile(contigs_fpath):
#            try:
#                os.remove(contigs_fpath)
#            except IOError as e:
#                logger.error('uploader_backend.remove_all: IOError when removing "%s": %s' % (fname, e.message))
#        try:
#            contigs_file.delete()
#            logger.info('uploader_backend.remove_all: Successfully removed "%s"' % fname)
#        except DatabaseError as e:
#            logger.error('uploader_backend.remove_all: DatabaseError when removing "%s": %s' % (fname, e.message))
#        except Exception as e:
#            logger.error('uploader_backend.remove_all: Exception when removing "%s": %s' % (fname, e.message))

@task()
def start_quast((args, quast_session, user_session)):
    command = ' '.join(args)
    print '=' * 100
    print 'Command:', command
    print '-' * 100
    logger.info('start_quast: running %s:' + command)

    link = quast_session.get_report_html_link()

    def send_result_mail(address, to_me, add_to_end='', fail=False, error_msg=None):
        if address is None or address == '':
            return

        if fail:
            subject = 'Failed' if to_me else 'Sorry, the assessment failed'
        else:
            subject = 'OK' if to_me else 'Quality assessment report'

        if quast_session.caption:
            subject += ' (%s)' % quast_session.caption

        arguments = {
            'caption': quast_session.caption,
            'link': link,
            'genome': quast_session.data_set.name if quast_session.data_set else '',
            'comment': quast_session.comment if quast_session.comment else '',
            'add_to_end': add_to_end,
            'error': error_msg
        }
        text_content = render_to_string('emails/report_ready.txt', arguments)

        arguments['add_to_end'] = add_to_end.replace('\n', '<br>\n')
        html_content = render_to_string('emails/report_ready.html', arguments)

        logger.info('Sending email to ' + str(address))
        email = EmailMultiAlternatives(subject, text_content, settings.SUPPORT_EMAIL, [address])
        email.attach_alternative(html_content, "text/html")
        email.send()

    my_email = settings.SUPPORT_EMAIL
    if quast_session.user:
        user_email = quast_session.user.email
    else:
        user_email = ''

    try:
        # if not settings.QUAST_DIRPATH in sys.path:
        #     sys.path.insert(1, settings.QUAST_DIRPATH)
        # import quast

        exit_code = os.system(' '.join(args))

    except Exception, e:
        logger.info('Run exit with exception')
        trace_back = traceback.format_exc()
        add_to_end = '\n' + \
                     '\n\nUser email: ' + str(user_email) + \
                     '\n\nSession key: ' + user_session.session_key + \
                     '\n\nArgs: ' + str(' '.join(args)) + \
                     '\n\nException: ' + str(e) + \
                     '\n\nTraceback: ' + str(trace_back)

        send_result_mail(my_email, to_me=True, add_to_end=add_to_end, fail=True)
        send_result_mail(user_email, to_me=False, fail=True)

    else:
        logger.info('Run finished with exit code=' + str(exit_code))
        add_to_end = '\n' + \
                     '\n\nUser email: ' + str(user_email) + \
                     '\n\nSession key: ' + user_session.session_key + \
                     '\n\nArgs: ' + str(' '.join(args))

        error_msg = None

        if exit_code != 0:  # Unsuccessful
            error_fpath = os.path.join(quast_session.get_dirpath(), settings.ERROR_LOG_FNAME)

            if os.path.isfile(error_fpath):
                with open(error_fpath) as error_f:
                    error_msg = error_f.read()

            send_result_mail(my_email, to_me=True, add_to_end=add_to_end, fail=True, error_msg=error_msg)
            send_result_mail(user_email, to_me=False, fail=True, error_msg=error_msg)

        else:  # OK
            # send_result_mail(my_email, to_me=True, add_to_end=add_to_end)
            send_result_mail(user_email, to_me=False)

        return exit_code, error_msg


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
#
#
# from datetime import datetime, timedelta
# from models import QuastSession
#
# logger = logging.getLogger('quast')
#
# @task()
# def delete_quast_sessions():
#     delete_before = datetime.now() - timedelta(days=5)
#     QuastSession.objects.filter(submitted=False, date__lt=delete_before).delete()
#     logger.info('deleted quast sessions before %s' % set(delete_before))
#     mailer.info('deleted quast sessions before %s' % set(delete_before))
