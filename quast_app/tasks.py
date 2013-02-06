import shutil
import sys
import os
import traceback
from celery.task import task
from django.conf import settings
from django.core.mail import send_mail

import logging
logger = logging.getLogger('quast')


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

    link = os.path.join(settings.REPORT_LINK_BASE, quast_session.link or quast_session.report_id)

    def send_result_mail(email, to_me, add_to_end='', fail=False):
        if email is None or email == '':
            return

        if fail:
            subject = 'Sorry, the assessment failed'
        else:
            subject = ('OK' if to_me else 'Quality assessment report')

        if quast_session.caption:
            subject += ' (%s)' % quast_session.caption
#        elif quast_session.data_set:
#            subject += ' (genome: %s)' % quast_session.data_set.name

        send_mail(
            subject=subject,
            message=
                (quast_session.caption + '\n\n' if quast_session.caption else '') +
                'http://quast.bioinf.spbau.ru' + link +
                ('\n\nGenome: ' + quast_session.data_set.name if quast_session.data_set else '') +
                ('\n\nComment: ' + quast_session.comment if quast_session.comment else '') +
                '\n\n\nIn case of any problems, feel free to reply to this message' +
                '\n\n<a href="quast.bioinf.spbau.ru">QUAST</a>: quality assessment tool for genome assemblies' +
                add_to_end,
            from_email=settings.SUPPORT_EMAIL,
            recipient_list=[email],
            fail_silently=True
        )

    my_email = 'vladsaveliev@me.com'
    if quast_session.user:
        user_email = quast_session.user.email
    else:
        user_email = ''

    try:
        if not settings.QUAST_DIRPATH in sys.path:
            sys.path.insert(1, settings.QUAST_DIRPATH)
        import quast

        result = quast.main(args[1:])

    except Exception as e:
        trace_back = traceback.format_exc()
        add_to_end = '\n'+ \
                     '\n\nUser email: ' + str(user_email) + \
                     '\n\nSession key: ' + user_session.session_key + \
                     '\n\nArgs: ' + str(args) + \
                     '\n\nException: ' + str(e) + \
                     '\n\nTraceback: ' + str(trace_back)

        send_result_mail(my_email, to_me=True, add_to_end=add_to_end, fail=True)
        send_result_mail(user_email, to_me=False, fail=True)
        raise e

    else:
        add_to_end = '\n' + \
                     '\n\nUser email: ' + user_email +\
                     '\n\nSession key: ' + user_session.session_key +\
                     '\n\nArgs: ' + str(args)

        send_result_mail(my_email, to_me=True, add_to_end=add_to_end)
        send_result_mail(user_email, to_me=False)

#        try:
#            shutil.rmtree(quast_session.get_evaluation_contigs_dirpath())
#        except Exception, e:
#            logger.error('Error removing evaluation_contig dir:' + e.message)

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