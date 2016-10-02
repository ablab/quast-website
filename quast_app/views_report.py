import json
import sys
from django.utils.html import escape
import os
from django.middleware.csrf import get_token
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest, Http404, HttpResponseRedirect
from django.conf import settings
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext

from tasks import start_quast
from models import UserSession, DataSet, QuastSession

import logging
logger = logging.getLogger('quast')
mailer = logging.getLogger('quast_mailer')


with open(settings.GLOSSARY_PATH) as f:
    glossary = f.read()

with open(settings.ICARUS_SCRIPT_FPATH) as f:
    icarus_script = f.read()

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
    tick_x                  = get('tick_x')
    coord_nx                = get('coordNx')
    coord_ngx               = get('coordNGx')
    coord_nax               = get('coordNAx')
    coord_ngax              = get('coordNGAx')
    icarus                  = get('icarus')

    if not settings.QUAST_DIRPATH in sys.path:
        sys.path.insert(1, settings.QUAST_DIRPATH)

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
        'tickX': tick_x,
        'coordNx': coord_nx,
        'coordNGx': coord_ngx,
        'coordNAx': coord_nax,
        'coordNGAx': coord_ngax,
        'icarus': icarus,

      # 'qualities': quality_dict,
      # 'mainMetrics': main_metrics,

        'glossary': glossary,
    }


def get_from_json(name, results_dirpath, is_required=False, msg=None):
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


def get_icarus_menu_response_dict(results_dirpath, is_contig_size_plot=False):
    if not os.path.isdir(results_dirpath):
        logger.error('no results directory %s ', results_dirpath)
        raise Exception('No results directory %s' % results_dirpath)

    response_dict = dict()
    use_old_template = False
    if get_from_json('div_references', results_dirpath):  # old reports
        use_old_template = True
        dict_keys = ['assemblies', 'links', 'div_references', 'th_assemblies', 'references']
    else:
        if get_from_json('menu_reference', results_dirpath):
            response_dict['reference'] = json.loads(get_from_json('menu_reference', results_dirpath))['menu_reference']
        elif get_from_json('table_references', results_dirpath):
            response_dict['table_references'] = json.loads(get_from_json('table_references', results_dirpath))['table_references']
        dict_keys = ['contig_size_html', 'assemblies']
    response_dict.update(dict((k, get_from_json(k, results_dirpath)) for k in dict_keys))
    response_dict['title'] = 'Icarus main menu'
    template_fpath = 'icarus/icarus-menu.html'
    if use_old_template:
        template_fpath = 'icarus/old-icarus-menu.html'

    return response_dict, template_fpath


def get_icarus_response_dict(results_dirpath, is_contig_size_plot=None):
    if not os.path.isdir(results_dirpath):
        logger.error('no results directory %s ', results_dirpath)
        raise Exception('No results directory %s' % results_dirpath)

    response_dict = dict()
    use_old_template = False
    data_json_fname = 'data_sizes' if is_contig_size_plot else 'data_alignments'
    response_dict['all_data'] = get_from_json(data_json_fname, results_dirpath)
    if not response_dict['all_data']:  # old reports
        use_old_template = True
        dict_keys = ['contig_sizes', 'size_threshold'] if is_contig_size_plot else ['contig_alignments', 'ms_selector']
    else:
        response_dict['ms_selector'] = json.loads(get_from_json('ms_selector', results_dirpath))['ms_selector'] if \
            get_from_json('ms_selector', results_dirpath) and not is_contig_size_plot else None
        response_dict['size_viewer'] = is_contig_size_plot
        dict_keys = ['size_threshold', 'num_contigs_warning'] if is_contig_size_plot else ['reference']
    response_dict.update(dict((k, get_from_json(k, results_dirpath)) for k in dict_keys))

    response_dict['title'] = 'Contig size viewer' if is_contig_size_plot else 'Contig alignment viewer'
    template_fpath = 'icarus/icarus-viewer.html'
    if use_old_template:
        template_fpath = 'icarus/old-icarus-viewer.html'
    return response_dict, template_fpath


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
    response_dict['download_link'] = qs.get_report_download_link()

    html_report_fpath = os.path.join(qs.get_dirpath(),
                                     settings.REGULAR_REPORT_DIRNAME,
                                     settings.HTML_REPORT_FNAME)
    response_dict['download'] = os.path.exists(html_report_fpath)
    if not response_dict['download']:
        logger.warn('download_report: html_report_fpath does not exist: \n%s' % html_report_fpath)


def __report_view_base(request, link):
    found_qs = QuastSession.objects.filter(link=link)
    if not found_qs.exists():
        found_qs = QuastSession.objects.filter(report_id=link)

    if not found_qs.exists():
        logger.debug('Quast session ' + link + ' not found, 404')
        raise Http404()

    qs = found_qs[0]
    logger.debug('Found quast sesstion ' + qs.report_id + ', location ' + qs.get_dirpath())

    future = start_quast.AsyncResult(qs.task_id)
    state = future.state

    exit_code, error = None, None

    if qs.report_id == '06_Sep_2016_17_33_47_245519':
        logger.debug('state=' + state + ', exit_code=' + str(exit_code) + ', but ' +
            'hardcoded ' + qs.report_id + ' to render success; ' \
            'setting state=' + state + ', exit_code=' + str(exit_code))
        state = 'SUCCESS'
        exit_code = 0
    elif state == 'SUCCESS':
        result = future.get()
        if isinstance(result, tuple):
            exit_code, error = result
        else:
            exit_code, error = result, None
        logger.debug('state=SUCCESS, exit_code=' + str(exit_code))

    return qs, state, exit_code, error


def __waiting_report(user_session, response_dict, request, qs, error, state):
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


def report_view(user_session, response_dict, request, link):
    qs, state, exit_code, error = __report_view_base(request, link)

    if state != 'SUCCESS' or exit_code != 0:
        logger.debug('state=' + state + ', exit_code=' + str(exit_code) + ', rendering WAITING page')
        return __waiting_report(user_session, response_dict, request, qs, error, state)

    logger.debug('state=' + state + ', exit_code=' + str(exit_code) + ', rendering REPORT page, ' +
                 'getting jsons from ' + qs.get_dirpath())
    response_dict.update(get_report_response_dict(qs.get_dirpath()))
    response_dict['comment'] = escape(qs.comment)
    response_dict['report_id'] = qs.report_id

    response_dict['hide_date'] = False

    __set_data_set_info(qs, response_dict)

    __set_title(qs, response_dict)

    __set_downloading(qs, response_dict)

    logger.debug('Loaded ' + str(response_dict))
    return render_to_response('assess-report.html', response_dict)


def download_report_view(request, link):
    qs, state, exit_code, error = __report_view_base(request, link)

    if state == 'SUCCESS' and exit_code == 0:
        regular_report_path = os.path.join(qs.get_dirpath(),
                                           settings.REGULAR_REPORT_DIRNAME)
        old_regular_report_path = os.path.join(qs.get_dirpath(),
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

        os.chdir(os.path.join(qs.get_dirpath(),
                              settings.REGULAR_REPORT_DIRNAME))

        report_fpath = settings.HTML_REPORT_FNAME
        report_aux_dirpath = settings.HTML_REPORT_AUX_DIRNAME
        zip_fname = qs.get_download_name() + '.zip'

        import zipfile, tempfile
        # from django.core.files.base import ContentFile
        from wsgiref.util import FileWrapper

        temp_file = tempfile.TemporaryFile()
        zip_file = zipfile.ZipFile(temp_file, 'w', zipfile.ZIP_DEFLATED, allowZip64=True)

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


def get_icarus_view(output_dirpath, is_menu=False, is_contig_size_plot=False, qs=None):
    response_dict = dict(settings.TEMPLATE_ARGS_BY_DEFAULT)
    get_response_fn = get_icarus_menu_response_dict if is_menu else get_icarus_response_dict
    report_dict, template_fpath = get_response_fn(output_dirpath, is_contig_size_plot=is_contig_size_plot)
    response_dict.update(report_dict)
    response_dict['hide_date'] = True
    if qs:
        response_dict['comment'] = escape(qs.comment)
        response_dict['report_id'] = qs.report_id

    return response_dict, render_to_response(template_fpath, response_dict)


def example_icarus_view(dir_name, caption, slug_name, is_menu=False, is_contig_size_plot=False):
    output_dirpath = os.path.join(settings.FILES_DIRPATH, dir_name, slug_name)
    report_dict, response = get_icarus_view(output_dirpath, is_menu, is_contig_size_plot)
    return response


def icarus_view(user_session, response_dict, request, link, is_menu=False, is_contig_size_plot=False):
    qs, state, exit_code, error = __report_view_base(request, link)

    if state != 'SUCCESS' or exit_code != 0:
        return __waiting_report(user_session, response_dict, request, qs, error, state)
    output_dirpath = qs.get_dirpath()
    report_dict, response = get_icarus_view(output_dirpath, is_menu, is_contig_size_plot)

    __set_downloading(qs, response_dict)

    return response


