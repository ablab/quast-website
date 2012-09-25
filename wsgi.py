"""
WSGI config for quast_website project.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.

Usually you will have the standard Django WSGI application here, but it also
might make sense to replace the whole Django WSGI application with a custom one
that later delegates to the Django one. For example, you could introduce WSGI
middleware here, or combine a Django application with an application of another
framework.

"""
import os
# prevent errors with 'print' commands
import sys

# sys.stdout = sys.stderr

# adopted from http://code.google.com/p/modwsgi/wiki/VirtualEnvironments
# def add_to_path(dirs):
#     # Remember original sys.path.
#     prev_sys_path = list(sys.path)

#     # Reorder sys.path so new directories at the front.
#     new_sys_path = []
#     for item in list(sys.path):
#         if item not in prev_sys_path:
#             new_sys_path.append(item)
#             sys.path.remove(item)
#     sys.path[:0] = new_sys_path

# add_to_path([
#     # os.path.normpath('/var/www/quality/virtualenv/lib/python2.7/site-packages'),
# ])
#from socketio.server import SocketIOServer

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

import djcelery
djcelery.setup_loader()

#PORT = 9000
#print 'Listening on port %s and on port 843 (flash policy server)' % PORT
#SocketIOServer(('', PORT), application, resource="socket.io").serve_forever()

# Apply WSGI middleware here.
# from helloworld.wsgi import HelloWorldApplication
# application = HelloWorldApplication(application)
