import time
from django.conf import settings
from django.db import DatabaseError

from models import UserSession


import logging

logger = logging.getLogger('quast')
mailer = logging.getLogger('quast_mailer')


def get_or_create_session(request, page):
    session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME, None)
    logger.info('request.COOKIES.get(settings.SESSION_COOKIE_NAME, None) = %s', session_key)

    session_key = request.session.session_key
    logger.info('Somebody opened %s with request.session.session_key = %s'
                % (page, session_key))

    if not session_key:
        from django.utils.crypto import get_random_string
        session_key = get_random_string(
            length=20,
            allowed_chars='abcdefghjkmnpqrstuvwxyz'
                          'ABCDEFGHJKLMNPQRSTUVWXYZ'
                          '123456789'
        )
        logger.warn('session_key is None. Generating new one: %s', session_key)

    tries = 10
    for i in range(tries):
        try:
            if not request.session.exists(session_key):
                request.session.create()
                break
        except DatabaseError as e:
            if i < tries - 1:
                logger.warn('Database is locked, try #%d' % i)
                time.sleep(2)
            else:
                logger.error('Database is locked (tried %d times)' % tries)
                raise

    logger.info('session.create(): session_key = %s' % session_key)
    if not session_key:
        logger.error('session_key is None')

    user_session = UserSession.get_or_create(session_key)
    return user_session