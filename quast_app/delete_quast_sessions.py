from datetime import datetime, timedelta
from models import QuastSession

import logging
logger = logging.getLogger('quast')
mailer = logging.getLogger('quast_mailer')

def delete_quast_sessions():
    delete_before = datetime.now() - timedelta(days=5)
    QuastSession.objects.filter(submitted=False, date__lt=delete_before).delete()
    logger.info('deleted quast sessions before %s' % set(delete_before))
    mailer.info('deleted quast sessions before %s' % set(delete_before))


if __name__ == '__main__':
    delete_quast_sessions()