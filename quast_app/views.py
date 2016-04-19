import json
import shutil
import datetime
import os
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from upload_backend import ContigsUploadBackend, ReferenceUploadBackend, GenesUploadBackend, OperonsUploadBackend
from django.conf import settings
from wsgiref.util import FileWrapper
# from django.core.files.base import ContentFile
import mimetypes

from views_report import get_report_response_dict, report_view, download_report_view, \
    icarus_view, icarus_alignment_viewer_view, icarus_contig_size_viewer_view
from views_reports import reports_view
from views_index import index_view

from models import UserSession, QuastSession, DataSet
from create_session import get_or_create_session, get_session

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


def changes(request):
    with open(settings.CHANGES_FPATH) as f:
        return HttpResponse(f.read(), content_type='text/plain')


def license(request):
    with open(settings.LICENSE_FPATH) as f:
        return HttpResponse(f.read(), content_type='text/plain')


def bib(request):
    with open(settings.BIB_FPATH) as f:
        return HttpResponse(f.read(), content_type='text/plain')


def benchmarking(request):
    return render_to_response('benchmarking.html', dict(settings.TEMPLATE_ARGS_BY_DEFAULT))


def example(request):
    response_dict = dict(settings.TEMPLATE_ARGS_BY_DEFAULT)
    response_dict.update(get_report_response_dict(settings.EXAMPLE_DIRPATH))
    response_dict['title'] = response_dict['caption'] = 'Sample report'
    response_dict['hide_date'] = True
    response_dict['data_set'] = {
        'title': 'E. coli, single-cell',
    }
    return render_to_response('report.html', response_dict)


def idba(request):
    response_dict = dict(settings.TEMPLATE_ARGS_BY_DEFAULT)
    response_dict.update(get_report_response_dict(os.path.join(settings.IDBA_DIRPATH)))

    response_dict['hide_date'] = True
    response_dict['data_set'] = {
        'title': 'E. coli, single-cell',
    }
    return render_to_response('idba.html', response_dict)


def index(request):
    user_session = get_or_create_session(request, 'index')
    return index_view(user_session, dict(settings.TEMPLATE_ARGS_BY_DEFAULT), request)


def report(request, link):
    user_session = get_session(request)
    return report_view(user_session, dict(settings.TEMPLATE_ARGS_BY_DEFAULT), request, link)

def download_report(request, link):
    return download_report_view(request, link)

def icarus(request, link):
    user_session = get_session(request)
    return icarus_view(user_session, dict(settings.TEMPLATE_ARGS_BY_DEFAULT), request, link)

def icarus_alignment_viewer(request, link):
    user_session = get_session(request)
    return icarus_alignment_viewer_view(user_session, dict(settings.TEMPLATE_ARGS_BY_DEFAULT), request, link)

def icarus_contig_size_viewer(request, link):
    user_session = get_session(request)
    return icarus_contig_size_viewer_view(user_session, dict(settings.TEMPLATE_ARGS_BY_DEFAULT), request, link)


def download_data_set(request, data_set_id, what, file_ext):
    us = get_session(request)
    data_sets = DataSet.get_common_data_sets() if us is None else us.get_all_allowed_dataset_set()

    if what == 'reference':
        data_set_id, file_ext = DataSet.split_seq_ext(data_set_id + file_ext)

    try:
        ds = data_sets.get(dirname=data_set_id)
    except DataSet.DoesNotExist:
        return HttpResponseNotFound('Data set %s was not found' % data_set_id)

    if what == 'reference':
        fpath = os.path.join(ds.get_dirpath(), ds.reference_fname)
        if DataSet.split_seq_ext(fpath)[1] != file_ext:
            return HttpResponseNotFound()

        return __download(fpath, data_set_id + file_ext)

    else:
        if what == 'genes':
            fpath = os.path.join(ds.get_dirpath(), ds.genes_fname)
        elif what == 'operons':
            fpath = os.path.join(ds.get_dirpath(), ds.operons_fname)
        else:
            return HttpResponseNotFound()

        if DataSet.split_genes_ext(fpath)[1] != file_ext:
            return HttpResponseNotFound()

        return __download(fpath, data_set_id + '_' + what + file_ext)


def __download(src_fpath, dist_fname):
    if not os.path.isfile(src_fpath):
        return HttpResponseNotFound()

    wrapper = FileWrapper(open(src_fpath, 'r'))
    response = HttpResponse(wrapper, content_type='application/x-download')
    response['Content-Length'] = os.path.getsize(src_fpath)
    response['Content-Disposition'] = 'attachment; ' \
                                      'filename=' + dist_fname or os.path.basename(src_fpath)
    return response


def reports(request):
    user_session = get_or_create_session(request, 'reports')
    return reports_view(user_session, dict(settings.TEMPLATE_ARGS_BY_DEFAULT), request)


def reorder_report_columns_ajax(request):
    user_session = get_session(request)
    if user_session is None:
        return HttpResponseNotFound('No user session for this session_key')

    try:
        report_id = request.GET['reportId']
    except KeyError:
        return HttpResponseNotFound('Value of reportId needed')

    try:
        order = map(int, request.GET['order'].split())  # 3 1 4 2
    except KeyError:
        return HttpResponseNotFound('Order was not provided')
    except ValueError:
        return HttpResponseNotFound('Incorrect order: should be space-separated numbers, like "3 1 5 3""')

    try:
        qs = QuastSession.objects.get(report_id=report_id)
    except QuastSession.DoesNotExist:
        return HttpResponseNotFound('Report %s not found' % report_id)

    with open(os.path.join(qs.get_dirpath(), 'report.json')) as report_f:
        report = json.loads(report_f.read())
        report['order'] = order

        # for group in report['report']:
        #     for metric in group[1]:
        #         values_by_asm_names = dict(zip(report['assembliesNames'], metric['values']))
        #         metric['values'] = [values_by_asm_names[name] for name in new_assembly_names]  # new order

        # report['assembliesNames'] = new_assembly_names

    with open(os.path.join(qs.get_dirpath(), 'report.json'), 'w') as report_f:
        report_f.write(json.dumps(report))

    return HttpResponse()


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
#            fpaths = [os.path.join(quast_session.get_contigs_dirpath(), c_f.fname)
#                      for c_f in quast_session.contigs_files.all()]
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
