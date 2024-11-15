import time
import traceback
from django.conf import settings
from django.db import DatabaseError

from models import UserSession


import logging

logger = logging.getLogger('quast')
mailer = logging.getLogger('quast_mailer')


def get_or_create_session(request, page):
  # session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME, None)
  # logger.info('request.COOKIES.get(settings.SESSION_COOKIE_NAME, None) = %s', session_key)

    session_key = request.session.session_key

  # logger.info('Somebody opened %s with request.session.session_key = %s'
  #             % (page, request.session.session_key))

  # if not session_key:
  #     from django.utils.crypto import get_random_string
  #     session_key = get_random_string(
  #         length=20,
  #         allowed_chars='abcdefghjkmnpqrstuvwxyz'
  #                       'ABCDEFGHJKLMNPQRSTUVWXYZ'
  #                       '123456789'
  #     )
  #     logger.warn('session_key is None. Generating new one: %s', session_key)

    if not session_key or not request.session.exists(session_key):
        tries = 10
        for i in range(tries):
            try:
                request.session.create()
                break
            except DatabaseError:
                if i < tries - 1:
                    logger.warn(traceback.format_exc())
                    logger.warn('Try #%d', i)
                    time.sleep(2)
                else:
                    logger.warn(traceback.format_exc())
                    logger.error('Tried %d times', tries)
                    raise

        session_key = request.session.session_key
        logger.info('session.create(): session_key = %s' % session_key)
        if not session_key:
            logger.error('session_key is None')
            raise Exception('session_key is None')

    user_session = UserSession.get_or_create(session_key)
    return user_session


def get_session(request):
    session_key = request.session.session_key
    if session_key and request.session.exists(session_key):
        try:
            return UserSession.objects.get(session_key=session_key)
        except UserSession.DoesNotExist:
            pass

    return None