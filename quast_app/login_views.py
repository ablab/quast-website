from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest, Http404
from django.conf import settings
from django.shortcuts import redirect

from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from models import User, UserSession, DataSet, QuastSession


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

    mailer.info('Email = %s' % email)


    # Current user session
    session_key = request.session.session_key
    try:
        user_session = UserSession.objects.get(session_key=session_key)
        if user_session.get_email() == email:
            mailer.info('user pressed login with the same login he already authorized with: %s' % email)
            # return HttpResponse('Authorized')
    # Unexpected
    except UserSession.DoesNotExist:
        msg = 'current user session with key=%s does not exist' % session_key
        logger.exception(msg)
        raise Exception(msg)
    except Exception:
        logger.exception()
        raise

    # User object that we trying to login
    if User.objects.filter(email=email).exists():
        new_user = User.objects.get(email=email)
    else:
        new_user = User.create(email)

    send_confirmation(new_user)
    return HttpResponse('Confirmation email sent')


def send_confirmation(user):
    link = '%slogin?email=%s&password=%s'\
           % (settings.ADDRESS, user.email, user.password)
    logger.info('link = %s' % link)

    send_mail(subject='QUAST. Confirmation of email address.',
              message='Hello!\n'
                      '\n'
                      'To authorize, follow the next link:\n'
                      '%s\n'
                      '\n'
                      'If you didn\'t want this email, please, just ignore it: it was probably sent by mistake.'
                      '\n'
                      '\n-'
                      'In case of any problems, feel free to reply to this message.'
                      % link,
              from_email=settings.SUPPORT_EMAIL,
              recipient_list=[user.email])


def login(request):
    if request.method != 'GET':
        raise Http404('Only GET allowed!')

    email = request.GET.get('email')
    password = request.GET.get('password')
    mailer.info('Email = %s, Password = %s' % (email, password))

    # User session
    session_key = request.session.session_key
    try:
        user_session = UserSession.objects.get(session_key=session_key)
    # Unexpected
    except UserSession.DoesNotExist:
        msg = 'current user session with key=%s does not exist' % session_key
        logger.exception(msg)
        raise Exception(msg)
    except Exception:
        logger.exception()
        raise

    # New user session
    if not User.objects.filter(email=email).exists():
        return HttpResponseBadRequest('User with this email does not exist')

    user = User.objects.get(email=email)

    if password == user.password or settings.PASSWORD and password == settings.PASSWORD:
        user_session.set_user(user)
        return redirect('quast_app.views.index')
    else:
        logger.warn('user tried to use a wrong password: %s instead of %s for %s',
                    password, user.password, email)
        return redirect('quast_app.views.index')














