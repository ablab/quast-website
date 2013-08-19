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


def get_report_response_dict(results_dirpath, caption, comment='', data_set_name='',
                             link='', set_title=False, safe=False):
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

    if caption:
        header = caption
    else:
        header = data_set_name

    return {
        'totalReport': total_report,
        'contigsLenghts': contigs_lengths,
        'alignedContigsLengths': aligned_contigs_lengths,
        'assembliesLengths': assemblies_lengths,
        'referenceLength': reference_length,
        'genesInContigs': genes_in_contigs,
        'operonsInContigs': operons_in_contigs,
        'gcInfo': gc_info,
        'download': False,

        'header': header,
        'setTitle': set_title,

        'dataSetName': data_set_name if safe else escape(data_set_name),
        'comment': comment if safe else escape(comment),
        'link': settings.REPORT_LINK_BASE + link,
        'downloadLink': settings.REPORT_LINK_BASE + 'download/' + link,

        'glossary': glossary,

        # 'qualities': quality_dict,
        # 'mainMetrics': main_metrics,
    }


def report_view(user_session, response_dict, request, link):
    found = QuastSession.objects.filter(link=link)
    if not found.exists():
        found = QuastSession.objects.filter(report_id=link)

    if found.exists():
        if request.method == 'GET':
            quast_session = found[0]
            if quast_session.user_session is None:
                quast_session.user_session = UserSession(user=quast_session.user)
                quast_session.save()

            # if quast_session.task_id == '1045104510450145' or quast_session.task_id == 1045104510450145:  # if the celery tasks have lost but we sure that this evaluated successfully
            #     result = None
            #     state = 'SUCCESS'
            # else:
            result = start_quast.AsyncResult(quast_session.task_id)
            state = result.state

            exit_code, error = None, None
            if state == 'SUCCESS':
                res = result.get()
                if isinstance(res, tuple):
                    exit_code, error = res
                else:
                    exit_code, error = res, None

                if exit_code == 0:
                    if quast_session.data_set and quast_session.data_set.remember:
                        data_set_name = quast_session.data_set.name
                    else:
                        data_set_name = ''

                    if data_set_name == '' and not quast_session.caption:
                        caption = 'Quality assessment'
                    else:
                        caption = quast_session.caption

                    response_dict.update(get_report_response_dict(
                        quast_session.get_dirpath(),
                        caption,
                        quast_session.comment,
                        data_set_name,
                        link,
                        set_title=True))

                    response_dict['report_id'] = quast_session.report_id

                    html_report_fpath = os.path.join(quast_session.get_dirpath(), settings.REGULAR_REPORT_DIRNAME, settings.HTML_REPORT_FNAME)
                    html_aux_report_dirpath = os.path.join(quast_session.get_dirpath(), settings.REGULAR_REPORT_DIRNAME, settings.HTML_REPORT_AUX_DIRNAME)
                    response_dict['download'] = os.path.exists(html_report_fpath) and os.path.exists(html_aux_report_dirpath)
                    if not response_dict['download']:
                        logger.warn('download_report: html_report_fpath and html_aux_report_dirpath does not exist: \n%s\n%s' % (html_report_fpath, html_aux_report_dirpath))

                    return render_to_response('assess-report.html', response_dict)

            state_repr = 'FAILURE'
            if result and state in task_state_map:
                state_repr = task_state_map[state]

            if state == 'SUCCESS' and exit_code != 0:
                state_repr = 'FAILURE'

            response_dict.update({
                'csrf_token': get_token(request),
                'session_key': request.session.session_key,
                'state': state_repr,
                'link': link,
                'report_id': quast_session.report_id,
                'comment': quast_session.comment,
                'caption': quast_session.caption,
                'data_set_name': quast_session.data_set.name if quast_session.data_set else None,
                'email': user_session.get_email() if user_session and
                         user_session == quast_session.user_session else None,
                'fnames': [c_f.fname for c_f in quast_session.contigs_files.all()],
                'error': error,
            })

            return render_to_response('waiting-report.html',
                                      response_dict,
                                      context_instance=RequestContext(request))

        if request.method == 'POST':
            # check status of quast session, return result
            raise Http404()

    else:
        raise Http404()


def download_report_view(request, link):
    found = QuastSession.objects.filter(link=link)
    if not found.exists():
        found = QuastSession.objects.filter(report_id=link)

    if found.exists():
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
                        return Http404()

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

                wrapper = FileWrapper(temp_file)
                response = HttpResponse(wrapper, content_type='application/zip')
                response['Content-Disposition'] = 'attachment; filename=%s' % zip_fname
                response['X-Sendfile'] = temp_file.tell()
                temp_file.seek(0)

                return response

    raise Http404()