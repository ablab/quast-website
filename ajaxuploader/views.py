from django.utils import simplejson as json
from django.core.serializers.json import DjangoJSONEncoder

from django.http import HttpResponse, HttpResponseBadRequest, Http404

from ajaxuploader.backends.local import LocalUploadBackend
from quast_app.models import UserSession

import logging
logger = logging.getLogger(__name__)


class AjaxFileUploader(object):
    def __init__(self, backend=None, **kwargs):
        if backend is None:
            backend = LocalUploadBackend
        self.get_backend = lambda: backend(**kwargs)

    def upload(self, request):
        return self._ajax_upload(request)

    def remove(self, request):
        return self._ajax_remove(request)

    def remove_all(self, request):
        return self._ajax_remove_all(request)

    def initialize_uploads(self, request):
        return self._ajax_initialize_uploads(request)

    def _ajax_upload(self, request):
        session_key = request.session.session_key
        try:
            user_session = UserSession.objects.get(session_key=session_key)
        except UserSession.DoesNotExist:
            return HttpResponseBadRequest('Can not recognise session key')

        if request.method == "POST":
            if request.is_ajax():
                # the file is stored raw in the request
                upload = request
                is_raw = True
                # AJAX Upload will pass the filename in the querystring if it
                # is the "advanced" ajax upload

                try:
                    filename = request.GET['qqfile']
                except KeyError:
                    return HttpResponseBadRequest('AJAX request is not valid')
            # not an ajax upload, so it was the "basic" iframe version with
            # submission via form
            else:
                is_raw = False
                if len(request.FILES) == 1:
                    # FILES is a dictionary in Django but Ajax Upload gives
                    # the uploaded file an ID based on a random number, so it
                    # cannot be guessed here in the code. Rather than editing
                    # Ajax Upload to pass the ID in the querystring, observe
                    # that each upload is a separate request, so FILES should
                    # only have one entry. Thus, we can just grab the first
                    # (and only) value in the dict.
                    upload = request.FILES.values()[0]
                else:
                    raise Http404("Bad Upload")
                filename = upload.name

            backend = self.get_backend()
            backend.user_session = user_session

            # custom filename handler
            filename = (backend.update_filename(request, filename)
                        or filename)
            # save the file
            backend.setup(filename)
            success = backend.upload(upload, filename, is_raw)
            # callback
            extra_context = backend.upload_complete(request, filename)

            # let Ajax Upload know whether we saved it or not
            ret_json = {'success': success, 'filename': filename}
            if extra_context is not None:
                ret_json.update(extra_context)

            return HttpResponse(json.dumps(ret_json, cls=DjangoJSONEncoder))


    def _ajax_remove(self, request):
        session_key = request.session.session_key
        try:
            user_session = UserSession.objects.get(session_key=session_key)
        except UserSession.DoesNotExist:
            logger.error('_ajax_remove: Can not recognise session key')
            return HttpResponse(json.dumps({
                   'success': False,
                   'message': 'Can not recognise session key'
                   }, cls=DjangoJSONEncoder))

        backend = self.get_backend()
        backend.user_session = user_session

        success, msg = backend.remove(request)
        return HttpResponse(json.dumps({
                   'success': success,
                   'message': msg
               }, cls=DjangoJSONEncoder))


    def _ajax_remove_all(self, request):
        success = False
        session_key = request.session.session_key
        try:
            user_session = UserSession.objects.get(session_key=session_key)
        except UserSession.DoesNotExist:
            logger.error('_ajax_remove_all: Can not recognise session key')
        else:
            backend = self.get_backend()
            backend.user_session = user_session
            success = backend.remove_all(request)

        #TODO response to nowhere
        return None # HttpResponse(json.dumps({'success': success}, cls=DjangoJSONEncoder))


    def _ajax_initialize_uploads(self, request):
        session_key = request.session.session_key
        try:
            user_session = UserSession.objects.get(session_key=session_key)
        except UserSession.DoesNotExist:
            return HttpResponseBadRequest('Can not recognise session key')

        backend = self.get_backend()
        backend.user_session = user_session
        uploads = backend.get_uploads(request)

        return HttpResponse(json.dumps({'uploads': uploads}, cls=DjangoJSONEncoder))
