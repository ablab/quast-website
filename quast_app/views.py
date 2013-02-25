
import shutil
import datetime
import os
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from upload_backend import ContigsUploadBackend, ReferenceUploadBackend, GenesUploadBackend, OperonsUploadBackend
from django.conf import settings

from views_report import get_report_response_dict, report_view, download_report_view
from views_reports import reports_view
from views_index import index_view

from models import UserSession, QuastSession
from create_session import get_or_create_session

import logging
logger = logging.getLogger('quast')
mailer = logging.getLogger('quast_mailer')


from ajaxuploader.views import AjaxFileUploader
contigs_uploader = AjaxFileUploader(backend=ContigsUploadBackend)
# reference_uploader = AjaxFileUploader(backend=ReferenceUploadBackend)
# genes_uploader = AjaxFileUploader(backend=GenesUploadBackend)
# operons_uploader = AjaxFileUploader(backend=OperonsUploadBackend)


def manual(request):
    with open(settings.MANUAL_FPATH) as f:
        return HttpResponse(f.read())


def license(request):
    with open(settings.LICENSE_FPATH) as f:
        return HttpResponse(f.read(), content_type='text/plain')


def bib(request):
    with open(settings.BIB_FPATH) as f:
        return HttpResponse(f.read(), content_type='text/plain')


def example(request):
    report_response_dict = get_report_response_dict(
        settings.EXAMPLE_DIRPATH,
        caption='Example',
        data_set_name='E. coli',
    )
    response_dict = dict(report_response_dict.items() + settings.TEMPLATE_ARGS_BY_DEFAULT.items())
    return render_to_response('example.html', response_dict)


def benchmarking(request):
    return render_to_response('benchmarking.html', settings.TEMPLATE_ARGS_BY_DEFAULT)


def idba(request):
    json_dirpath = os.path.join(settings.ECOLI_DIRPATH)
    report_response_dict = get_report_response_dict(
        json_dirpath,
        caption='SPAdes - IDBA collaboration',
        comment='',
        data_set_name='E.coli',
        link='')
    response_dict = dict(report_response_dict.items() + settings.TEMPLATE_ARGS_BY_DEFAULT.items())
    return render_to_response('ecoli.html', response_dict)


def index(request):
    user_session = get_or_create_session(request, 'index')
    return index_view(user_session, settings.TEMPLATE_ARGS_BY_DEFAULT, request)


def report(request, link):
    user_session = get_or_create_session(request, 'report')
    return report_view(user_session, settings.TEMPLATE_ARGS_BY_DEFAULT, request, link)


def download_report(request, link):
    return download_report_view(request, link)


def reports(request):
    user_session = get_or_create_session(request, 'reports')
    return reports_view(user_session, settings.TEMPLATE_ARGS_BY_DEFAULT, request)


def delete_session(request):
    try:
        report_id = request.GET['reportId']
    except KeyError:
        logger.error('Request must contain reportId')
        return HttpResponseBadRequest('Request must contain reportId')

    if not report_id:
        logger.error('reportId is None')
        return HttpResponseBadRequest('reportId is None')

    if report_id == u'undefined':
        logger.error('reportId = "undefined"')
        return HttpResponseBadRequest('reportId = "undefined"')

    try:
        quast_session = QuastSession.objects.get(report_id=report_id)
    except QuastSession.DoesNotExist:
        logger.error('No quast session with report_id=%s' % report_id)
        return HttpResponseBadRequest('wrong reportId: no such quast-session')

    if not quast_session.submitted:
#        if quast_session.contigs_files:
#            fpaths = [os.path.join(quast_session.get_contigs_dirpath(), c_f.fname) for c_f in quast_session.contigs_files.all()]
#            for fpath in fpaths:
#                if os.path.exists(fpath):
#                    try:
#                        os.remove(fpath)
#                        logger.info('Deleted contigs_file %s' % fpath)
#                    except Exception, e:
#                        logger.warn('Error deleting contigs file %s: %s' % (fpath, e.message))

        logger.info('Deleting quast_session with id=%s, dirpath=%s', report_id, quast_session.get_dirpath())

        if os.path.isdir(quast_session.get_dirpath()):
            shutil.rmtree(quast_session.get_dirpath())
        else:
            logger.error('directory does not exist')
        quast_session.delete()
#    else:
#        logger.info('Quast session with id=%s wasn\'t submitted, not deleting' % report_id)
    return HttpResponse()


#    try:
#        quast_session = QuastSession.objects.get(report_id=report_id)
#    except QuastSession.DoesNotExist:
#        logger.error('No quast session with report_id=%s' % report_id)
#        return HttpResponseBadRequest('wrong reportId: no such quast-session')
#
#    if not quast_session.submitted:


#def get_evaluate_response_dict(request, user_session, url):
#    contigs_fnames = [c_f.fname for c_f in user_session.contigsfile_set.all()]
#
#    if request.method == 'POST':
#        data_set_form = DatasetForm(request.POST)
#        data_set_form.set_user_session(user_session)
#        #        data_set_form.fields['name_selected'].choices = dataset_choices
#        if data_set_form.is_valid():
#            from datetime import datetime
#            now_datetime = datetime.now()
#            now_str = now_datetime.strftime('%d_%b_%Y_%H:%M:%S.%f')
#
#            min_contig = data_set_form.cleaned_data['min_contig']
#            request.session['min_contig'] = min_contig
#            data_set = get_dataset(request, data_set_form, now_str)
#            quast_session = start_quast_session(user_session, data_set, min_contig, now_datetime)
#
#            return redirect(url, after_evaluation=True)
#
#        else:
#            min_contig = request.session.get('min_contig') or qconfig.min_contig
#            request.session['min_contig'] = min_contig
#            data_set_form.set_min_contig(min_contig)
#
#        #            return render_to_response('reports.html', {
#        #                'glossary': glossary,
#        #                'csrf_token': get_token(request),
#        #                'session_key': user_session_key,
#        #                'contigs_fnames': contigs_fnames,
#        #                'data_set_form': data_set_form,
#        #                'report_id': quast_session.report_id,
#        #                }, context_instance = RequestContext(request))
#    else:
#        data_set_form = DatasetForm()
#        min_contig = request.session.get('min_contig') or qconfig.min_contig
#        data_set_form.set_min_contig(min_contig)
#
#    #        data_set_form.fields['name_selected'].choices = dataset_choices
#
#    response_dict = settings.TEMPLATE_ARGS_BY_DEFAULT
#    response_dict = dict(response_dict.items() + {
#        'csrf_token': get_token(request),
#        'contigs_fnames': contigs_fnames,
#        'data_set_form': data_set_form,
#    }.items())
#
#    return response_dict



#def evaluate(request):
#    if not request.session.exists(request.session.session_key):
#        request.session.create()
#
#    user_session_key = request.session.session_key
#    try:
#        user_session = UserSession.objects.get(session_key=user_session_key)
#    except UserSession.DoesNotExist:
#        user_session = create_user_session(user_session_key)
#
#    response_dict = get_evaluate_response_dict(request, user_session, '/evaluate/')
#    return render_to_response('evaluate.html', response_dict, context_instance = RequestContext(request))

