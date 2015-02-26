import sys
from django.utils.html import escape
import os
from django.middleware.csrf import get_token
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest, Http404, HttpResponseRedirect
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext

from tasks import start_quast
from models import UserSession, DataSet, QuastSession

import logging
logger = logging.getLogger('quast')
mailer = logging.getLogger('quast_mailer')


glossary = '{}'
with open(settings.GLOSSARY_PATH) as f:
    glossary = f.read()


task_state_map = {
    'PENDING': 'PENDING',
    'STARTED': 'PENDING',
    'FAILURE': 'FAILURE',
    'SUCCESS': 'SUCCESS',
}


def get_report_response_dict(results_dirpath):
    if not os.path.isdir(results_dirpath):
        logger.error('no results directory %s ', results_dirpath)
        raise Exception('No results directory %s' % results_dirpath)

    def get(name, is_required=False, msg=None):
        contents = ''
        fname = name + '.json'
        try:
            f = open(os.path.join(results_dirpath, fname))
            contents = f.read()
        except IOError:
            if is_required:
                logger.exception('%s is not found.' % fname)
                raise Exception('%s is not found.' % fname)
        return contents

    total_report            = get('report', is_required=True)
    contigs_lengths         = get('contigs_lengths', is_required=True)
    reference_length        = get('ref_length')
    assemblies_lengths      = get('assemblies_lengths')
    aligned_contigs_lengths = get('aligned_contigs_lengths')
    genes_in_contigs        = get('genes_in_contigs')
    operons_in_contigs      = get('operons_in_contigs')
    gc_info                 = get('gc')

    if not settings.QUAST_DIRPATH in sys.path:
        sys.path.insert(1, settings.QUAST_DIRPATH)
    from libs import reporting

    #    import json
    #    quality_dict = json.dumps(reporting.Fields.quality_dict)
    #    main_metrics = json.dumps(reporting.get_main_metrics())

    return {
        'totalReport': total_report,
        'contigsLengths': contigs_lengths,
        'alignedContigsLengths': aligned_contigs_lengths,
        'assembliesLengths': assemblies_lengths,
        'referenceLength': reference_length,
        'genesInContigs': genes_in_contigs,
        'operonsInContigs': operons_in_contigs,
        'gcInfo': gc_info,

      # 'qualities': quality_dict,
      # 'mainMetrics': main_metrics,

        'glossary': glossary,
    }


def __set_data_set_info(qs, response_dict):
    data_set_title = ''
    if qs.data_set:
        if qs.data_set.remember:
            data_set_title = escape(qs.data_set.name)

        response_dict['data_set'] = {
            'title': data_set_title,
            'id': qs.data_set.dirname,
            'reference_ext': DataSet.split_seq_ext(qs.data_set.reference_fname)[1],
            'genes_ext': DataSet.split_genes_ext(qs.data_set.genes_fname)[1] if qs.data_set.genes_fname else None,
            'operons_ext': DataSet.split_genes_ext(qs.data_set.operons_fname)[1] if qs.data_set.operons_fname else None,
        }


def __set_title(qs, response_dict):
    if qs.caption:
        title = escape(qs.caption)
    else:
        if 'data_set' in response_dict and response_dict['data_set']['title']:
            title = response_dict['data_set']['title']
        else:
            title = 'Quality assessment'

    response_dict['title'] = title
    response_dict['caption'] = title


def __set_downloading(qs, response_dict):
    response_dict['download_link'] = settings.REPORT_LINK_BASE + 'download/' + qs.link

    html_report_fpath = os.path.join(qs.get_dirpath(),
                                     settings.REGULAR_REPORT_DIRNAME,
                                     settings.HTML_REPORT_FNAME)
    html_aux_report_dirpath = os.path.join(qs.get_dirpath(),
                                           settings.REGULAR_REPORT_DIRNAME,
                                           settings.HTML_REPORT_AUX_DIRNAME)
    response_dict['download'] = os.path.exists(html_report_fpath) and\
                                os.path.exists(html_aux_report_dirpath)
    if not response_dict['download']:
        logger.warn('download_report: html_report_fpath and html_aux_report_dirpath'
                    ' does not exist: \n%s\n%s' % (html_report_fpath, html_aux_report_dirpath))


def report_view(user_session, response_dict, request, link):
    found_qs = QuastSession.objects.filter(link=link)
    if not found_qs.exists():
        found_qs = QuastSession.objects.filter(report_id=link)

    if not found_qs.exists():
        raise Http404()

    if request.method == 'POST':
        # check status of quast session, return result
        pass

    if request.method == 'GET':
        qs = found_qs[0]
        if qs.user_session is None:
            qs.user_session = UserSession(user=qs.user)
            qs.save()

      # If the celery tasks have lost but we sure that this evaluated successfully:
      # if quast_session.task_id == '1045104510450145' or quast_session.task_id == 1045104510450145:
      #     result = None
      #     state = 'SUCCESS'
      # else:
        future = start_quast.AsyncResult(qs.task_id)
        state = future.state

        exit_code, error = None, None
        if state == 'SUCCESS':
            result = future.get()
            if isinstance(result, tuple):
                exit_code, error = result
            else:
                exit_code, error = result, None

        if state != 'SUCCESS' or exit_code != 0:
            response_dict.update({
                'csrf_token': get_token(request),
                'session_key': request.session.session_key,
                'link': qs.link,
                'report_id': qs.report_id,
                'comment': qs.comment,
                'caption': qs.caption,
                'data_set_name': qs.data_set.name if qs.data_set else None,
                'email': user_session.get_email() if user_session and
                         user_session == qs.user_session else None,
                'fnames': [c_f.fname for c_f in qs.contigs_files.all()],
                'error': error,
                'state': {
                    'PENDING': 'PENDING',
                    'STARTED': 'PENDING',
                    'FAILURE': 'FAILURE',
                  }.get(state, 'FAILURE'),
            })

            return render_to_response('waiting-report.html', response_dict,
                context_instance=RequestContext(request))

        response_dict.update(get_report_response_dict(qs.get_dirpath()))
        response_dict['comment'] = escape(qs.comment)
        response_dict['report_id'] = qs.report_id

        response_dict['hide_date'] = False

        __set_data_set_info(qs, response_dict)

        __set_title(qs, response_dict)

        __set_downloading(qs, response_dict)

        return render_to_response('assess-report.html', response_dict)


def download_report_view(request, link):
    found = QuastSession.objects.filter(link=link)
    if not found.exists():
        found = QuastSession.objects.filter(report_id=link)

    if not found.exists():
        raise Http404()

    quast_session = found[0]

    # if quast_session.task_id == '1045104510450145' or\
    #    quast_session.task_id == 1045104510450145:
    #     # If the celery tasks have lost but we sure that this evaluated successfully
    #     # If the next time you need to restore tasks already evaluated but the database
    #     # is lost, put this task id to the quastsession record.
    #     result = None
    #     state = 'SUCCESS'
    # else:
    result = start_quast.AsyncResult(quast_session.task_id)
    state = result.state

    if state == 'SUCCESS':
        res = result.get()
        if isinstance(res, tuple):
            exit_code, error = res
        else:
            exit_code, error = res, None

        if exit_code == 0:
            regular_report_path = os.path.join(quast_session.get_dirpath(),
                                               settings.REGULAR_REPORT_DIRNAME)
            old_regular_report_path = os.path.join(quast_session.get_dirpath(),
                                                   'regular_report')

            if not os.path.exists(regular_report_path):
                if os.path.exists(old_regular_report_path):
                    os.rename(old_regular_report_path, regular_report_path)
                else:
                    logger.warning('quast_app_download_report:'
                                   ' User tried to download report, '
                                   'but neither %s nor %s exists' %
                                   (settings.REGULAR_REPORT_DIRNAME, 'regular_report'))
                    raise Http404()

            os.chdir(os.path.join(quast_session.get_dirpath(),
                                  settings.REGULAR_REPORT_DIRNAME))

            report_fpath = settings.HTML_REPORT_FNAME
            report_aux_dirpath = settings.HTML_REPORT_AUX_DIRNAME
            zip_fname = quast_session.get_download_name() + '.zip'
            
            import zipfile, tempfile
            from django.core.servers.basehttp import FileWrapper
            temp_file = tempfile.TemporaryFile()
            zip_file = zipfile.ZipFile(temp_file, 'w', zipfile.ZIP_DEFLATED)

            zip_file.write(report_fpath)

            def zip_dir(dirpath):
                for root, dirs, files in os.walk(dirpath):
                    for file in files:
                        zip_file.write(os.path.join(root, file))
                    for dir in dirs:
                        zip_dir(dir)
            zip_dir(report_aux_dirpath)

            os.chdir('..')
            zip_dir(settings.REGULAR_REPORT_DIRNAME)
            zip_file.close()

            temp_file.flush()
            content_len = temp_file.tell()
            temp_file.seek(0)
            wrapper = FileWrapper(temp_file)
            response = HttpResponse(wrapper, content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename=%s' % zip_fname
            response['Content-Length'] = content_len

            return response
