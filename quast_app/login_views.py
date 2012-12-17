from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest, Http404
from django.conf import settings
from django.shortcuts import redirect

from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from models import User, UserSession, DataSet, QuastSession
from create_session import get_or_create_session


import logging
logger = logging.getLogger('quast')
mailer = logging.getLogger('quast_mailer')


def ask_password(request):
    email = request.GET.get('email')
    if email is None:
        logger.error('No email in GET request')
        return HttpResponseBadRequest('No email in GET request')

    if email == '':
        return HttpResponseBadRequest('Please, specify your email')
    try:
        validate_email(email)
    except ValidationError:
        return HttpResponseBadRequest('Incorrect email')


    # Current user session
    session_key = request.session.session_key
    try:
        user_session = UserSession.objects.get(session_key=session_key)
        if user_session.get_email() == email:
            mailer.info('User pressed login with the same login he already authorized with: %s' % email)
    # Cookies turned off
    except UserSession.DoesNotExist:
        pass
        # logger.warn('current user session with key=%s does not exist, creating new one', session_key)
        # user_session = get_or_create_session(request, 'ask_password')
    except Exception:
        logger.exception()

    # User object that we trying to login
    if User.objects.filter(email=email).exists():
        new_user = User.objects.get(email=email)
    else:
        new_user = User.create(email)

    send_confirmation(new_user)
    return HttpResponse('Confirmation message sent. Please, check you email.<br>'
                        'If you do not receive a message, please check your junk mail folder.')


def send_confirmation(user):
    link = '%slogin?email=%s&password=%s'\
           % (settings.ADDRESS, user.email, user.password)
    logger.info('link = %s' % link)

    send_mail(subject='Confirmation of email address',
              message='Hello!\n'
                      '\n'
                      'To authorize, follow the link:\n'
                      '%s\n'
                      '\n'
                      'If you didn\'t want this email, please, just ignore it: it was probably sent by mistake.'
                      '\n'
                      '\n---'
                      '\nIn case of any problems, feel free to reply to this message,'
                      '\nQUAST team'
                      % link,
              from_email=settings.SUPPORT_EMAIL,
              recipient_list=[user.email])

    mailer.info('Confirmation message was sent to %s with password %s', user.email, user.password)


def login(request):
    if request.method != 'GET':
        raise Http404('Only GET allowed!')

    email = request.GET.get('email')
    if not email:
        mailer.info('Login: no email')
        return HttpResponseBadRequest('Please, specify your email')
    try:
        validate_email(email)
    except ValidationError:
        mailer.info('Login: incorrect email: %s', email)
        return HttpResponseBadRequest('Incorrect email')

    password = request.GET.get('password')

    # User session
    # session_key = request.session.session_key
    # try:
    #     user_session = UserSession.objects.get(session_key=session_key)
    # # Unexpected
    # except UserSession.DoesNotExist:
    #     msg = 'current user session with key=%s does not exist' % session_key
    #     logger.exception(msg)
    #     raise Exception(msg)
    # except Exception:
    #     logger.exception()
    #     raise

    # New user
    if not User.objects.filter(email=email).exists():
        mailer.info('User with this email does not exist: email = %s and password = %s', email, password)
        return HttpResponseBadRequest('User with this email does not exist')

    user = User.objects.get(email=email)

    if password == user.password or \
       settings.DEBUG and password == settings.DEBUG_PASSWORD:

        user_session = get_or_create_session(request, 'login')
        user_session.set_user(user)
        user.generate_password()

        mailer.info('User signed in with email = %s and password = %s', email, password)
        return redirect('quast_app.views.index')

    else:
        mailer.info('User tried to log in with a wrong password: %s instead of %s for %s',
                    password, user.password, email)
        return redirect('quast_app.views.index')














