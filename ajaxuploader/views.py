import json
from django.core.serializers.json import DjangoJSONEncoder

from django.http import HttpResponse, HttpResponseBadRequest, Http404, HttpResponseForbidden

from ajaxuploader.backends.local import LocalUploadBackend
from quast_app.models import UserSession

import logging

logger = logging.getLogger('quast')


class AjaxFileUploader(object):
    def __init__(self, backend=None, max_size=None, **kwargs):
        if backend is None:
            backend = LocalUploadBackend
        self.get_backend = lambda: backend(**kwargs)
        self.max_size = max_size

    def upload(self, request):
        logger.info('ajaxuploaer.views.upload')
        return self._ajax_upload(request)

    def remove(self, request):
        logger.info('ajaxuploaer.views.remove')
        return self._ajax_remove(request)

    def remove_all(self, request):
        logger.info('ajaxuploaer.views.remove_all')
        return self._ajax_remove_all(request)

    def initialize_uploads(self, request):
        logger.info('ajaxuploaer.views.initialize_uploads')
        return self._ajax_initialize_uploads(request)

    def __extract_report_id(self, request):
    #        session_key = request.session.session_key
    #        try:
    #            user_session = UserSession.objects.get(session_key=session_key)
    #        except UserSession.DoesNotExist:
    #            logging.error('Cannot recognise session key: %s', str(session_key))
    #            return HttpResponseBadRequest('Cannot recognise session key')

        try:
            report_id = request.GET['reportId']
        except KeyError:
            logger.error('Request must contain reportId')
            return None

        if not report_id:
            logger.error('reportId is None')
            return None

        if report_id == u'undefined':
            logger.error('reportId = "undefined"')
            return None

        #        try:
        #            quast_session = QuastSession.objects.get(report_id=report_id)
        #        except QuastSession.DoesNotExist:
        #            logger.error('uploader_backend.update_filename: No quast session with report_id=%s' % report_id)
        #            return None

        return report_id

    def _ajax_upload(self, request):
        if request.method == "POST":
            if request.is_ajax():
                logger.info('request is ajax')

                # the file is stored raw in the request
                upload = request
                is_raw = True
                # AJAX Upload will pass the filename in the querystring if it
                # is the "advanced" ajax upload

                try:
                    filename = request.GET['qqfile']
                except KeyError:
                    logger.error('AJAX request does not contain qqfile')
                    return HttpResponseBadRequest('AJAX request is not valid: must contain "qqfile"')
            # not an ajax upload, so it was the "basic" iframe version with
            # submission via form
            else:
                logger.info('request is not ajax, getting request.FILES')
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
                    logger.error('len(request.FILES) is %d' % len(request.FILES))
                    raise Http404("Bad Upload")
                filename = upload.name

            logger.info('uploading file %s' % filename)

            backend = self.get_backend()
            report_id = self.__extract_report_id(request)
            if not report_id:
                logger.error('no reportId')
                return HttpResponseBadRequest('No reportId')
            logger.info('report_id=%s' % report_id)

            ok = backend.set_report_id(report_id)
            if not ok:
                logger.error('no quast session')
                return HttpResponseBadRequest('No quast session, please reload the page')

            # custom filename handler
            filename = (backend.update_filename(request, filename) or filename)
            # save the file
            if not backend.setup(filename):
                logger.error('setup for %s failed' % filename)
                return HttpResponseBadRequest('No quast session contigs directory, please reload the page')
            else:
                logger.info('setup for %s: success' % filename)

            try:
                size_ok = backend.upload(upload, filename, is_raw, max_size=self.max_size)
            except:
                success = False
                size_ok = None
            else:
                success = size_ok

            # callback
            extra_context = backend.upload_complete(request, filename)

            # let Ajax Upload know whether we saved it or not
            ret_json = {'success': success, 'sizeExceeded': not size_ok, 'filename': filename}
            if extra_context is not None:
                ret_json.update(extra_context)

            return HttpResponse(json.dumps(ret_json, cls=DjangoJSONEncoder))

        raise Http404

    def _ajax_remove(self, request):
    #        session_key = request.session.session_key
    #        try:
    #            user_session = UserSession.objects.get(session_key=session_key)
    #        except UserSession.DoesNotExist:
    #            logger.error('_ajax_remove: Can not recognise session key')
    #            return HttpResponse(json.dumps({
    #                   'success': False,
    #                   'message': 'Can not recognise session key'
    #                   }, cls=DjangoJSONEncoder))

        backend = self.get_backend()
        report_id = self.__extract_report_id(request)
        if not report_id:
            success = False
            msg = 'No report id'
        else:
            res = backend.set_report_id(report_id)
            if not res:
                success = False
                msg = 'No quast session'
            else:
                success, msg = backend.remove(request)

        return HttpResponse(json.dumps({
                               'success': success,
                               'message': msg
                            }, cls=DjangoJSONEncoder))

    def _ajax_remove_all(self, request):
        success = False
        #        session_key = request.session.session_key
        #        try:
        #            user_session = UserSession.objects.get(session_key=session_key)
        #        except UserSession.DoesNotExist:
        #            logger.error('_ajax_remove_all: Can not recognise session key')
        #        else:

        backend = self.get_backend()
        report_id = self.__extract_report_id(request)
        if not report_id:
            return HttpResponseBadRequest('No report id')
        res = backend.set_report_id(report_id)
        if not res:
            return HttpResponseBadRequest('No quast session')

        success = backend.remove_all(request)

        #TODO response to nowhere
        return None # HttpResponse(json.dumps({'success': success}, cls=DjangoJSONEncoder))

    def _ajax_initialize_uploads(self, request):
    #        session_key = request.session.session_key
    #        try:
    #            user_session = UserSession.objects.get(session_key=session_key)
    #        except UserSession.DoesNotExist:
    #            return HttpResponseBadRequest('Can not recognise session key')

        backend = self.get_backend()
        report_id = self.__extract_report_id(request)
        if not report_id:
            return HttpResponseBadRequest('No report id')
        res = backend.set_report_id(report_id)
        if not res:
            return HttpResponseBadRequest('No quast session')

        uploads = backend.get_uploads(request)

        return HttpResponse(json.dumps({'uploads': uploads}, cls=DjangoJSONEncoder))
