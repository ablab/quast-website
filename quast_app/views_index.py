from django.core.urlresolvers import reverse
import os
from django.middleware.csrf import get_token
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest, Http404, HttpResponseRedirect
from django.conf import settings

from views_report import get_report_response_dict
from views_reports import get_reports_response_dict
from models import QuastSession, DataSet
from forms import DataSetForm

import logging
logger = logging.getLogger('quast')
mailer = logging.getLogger('quast_mailer')


def index_view(us, response_dict, request):
    # Evaluation
    if request.method == 'POST':
        log_msg = 'Somebody posted a form:'
        for k, v in request.POST.items():
            if k == 'contigs:':
                log_msg += '\n\t%s' % k
                for contig in v.split('\n'):
                    log_msg += '\n\t\t%s' % contig
            else:
                log_msg += '\n\t%s:\t%s' % (str(k), str(v))
        # mailer.info(log_msg)

        form = DataSetForm(us, request.POST)

        report_id = form.data.get('report_id')
        if not report_id:
            logger.error('data_set_form.data.get(\'report_id\') is None')
            return HttpResponseBadRequest('No report_id in form')

        try:
            qs = QuastSession.objects.get(report_id=report_id)
        except QuastSession.DoesNotExist:
            logger.error('QuastSession with report_id=%s does not exist' % report_id)
            return HttpResponseBadRequest('No quast session with report_id=%s' % report_id)
        else:
            #TODO: Temporary, used because user_session was always deleted when registering a user
            if not qs.user_session:
                qs.user_session = us
            #TODO: End of temporary

            # Contigs fnames from this form
            # contigs_in_form = data_set_form.data.get('contigs')
            #
            # split = contigs_in_form.split('\r\n')
            # if len(split) == 1:
            #     split = contigs_in_form.split('\n')
            # if len(split) == 1:
            #     logger.error('No contigs fnames got from "data_set_form.contigs": the value got is %s', str(contigs_in_form))
            #     return HttpResponseBadRequest("Error: no contigs loaded")

            # contigs_fnames = split[:-1]

        if form.is_valid():
            qs.submitted = True

            qs.min_contig = form.cleaned_data['min_contig']
            qs.scaffolds = form.cleaned_data['scaffolds']
            qs.eukaryotic = form.cleaned_data['domain'] == 'True'
            qs.estimated_ref_size = form.cleaned_data['estimated_ref_size']
            qs.find_genes = form.cleaned_data['find_genes']
            qs.data_set = get_data_set(request, form, us, default_name=qs.report_id)

            us.set_min_contig(qs.min_contig)
            us.set_scaffolds(qs.scaffolds)
            us.set_eukaryotic(qs.eukaryotic)
            us.set_estimated_ref_size(qs.estimated_ref_size)
            us.set_find_genes(qs.find_genes)
            us.set_default_data_set(qs.data_set)
            us.save()

            qs.comment = form.cleaned_data.get('comment')
            qs.caption = form.cleaned_data.get('caption')
            qs.generate_link()
            qs.save()

            logger.info('quast_app.views.index.POST: '
                        'caption = %s, link = %s, data set = %s, '
                        'min_contig = %d, scaffolds = %r, eukaryotic = %r, find_genes = %r',
                        qs.caption, qs.link, qs.data_set.name if qs.data_set else '<unknown>',
                        qs.min_contig, qs.scaffolds, qs.eukaryotic, qs.find_genes)

            # Starting Quast
            start_quast_session(us, qs)
            # return HttpResponseRedirect(reverse('True}))

            request.session['after_evaluation'] = True
            # return redirect('quast_app.views.index')
            return HttpResponseRedirect(reverse("quast_app.views.index"))

            # return redirect('quast_app.views.report', link=quast_session.link)
        else:
            logger.info('quast_app.views.index.POST: form invalid, errors are: = %s', str(form.errors.items()))

    elif request.method == 'GET':
        # min_contig = request.session.get('min_contig') or qconfig.min_contig
        # scaffolds = request.session.get('scaffolds') or False
        # eukaryotic = request.session.get('eukaryotic') or False
        # estimated_ref_size = request.session.get('estimated_ref_size') or None
        # find_genes = request.session.get('find_genes') or False

        qs = QuastSession.create(us)
        form = DataSetForm(us, initial={
            'report_id': qs.report_id,
            'name_selected': qs.data_set.name if qs.data_set else None,
            'min_contig': qs.min_contig,
            'scaffolds': qs.scaffolds,
            'domain': qs.eukaryotic,
            'estimated_ref_size': qs.estimated_ref_size,
            'find_genes': qs.find_genes,
        })

        response_dict['report_id'] = qs.report_id

        # Default data set for this user
        # if user_session.get_default_data_set():
        #     default_data_set_name = user_session.get_default_data_set().name
        # else:
        #     default_data_set_name = request.session.get('default_data_set_name') or ''
        #     if default_data_set_name:
        #         try:
        #             default_data_set = DataSet.objects.get(name=default_data_set_name)
        #             user_session.set_default_data_set(default_data_set)
        #         except DataSet.DoesNotExist:
        #             pass
        #
        # form.set_default_data_set_name(default_data_set_name)

    else:
        logger.warn('Request method is %s' % request.method)
        return HttpResponseBadRequest("GET and POST are only supported here")

    # uploaded_contigs_fnames = [c_f.fname for c_f in user_session.contigsfile_set.all()]

    response_dict.update({
        'csrf_token': get_token(request),
        'contigs_fnames': [],
        'qs_form': form,
        'email': us.get_email(),
        'session_key': us.session_key,
        'is_authorized': us.user is not None,
    })

    # REPORTS
    response_dict.update(get_reports_response_dict(
        us,
        after_evaluation=request.session.get('after_evaluation', False),
        limit=settings.REPORTS_SHOW_LIMIT))

    request.session['after_evaluation'] = False

    # EXAMPLE
    response_dict.update(get_report_response_dict(settings.EXAMPLE_DIRPATH))
    response_dict['hide_date'] = True
    response_dict['data_set'] = {
        'title': 'E. coli, single-cell',
    }

    return render_to_response(
        'index.html',
        response_dict,
        context_instance=RequestContext(request))


def get_data_set(request, data_set_form, user_session, default_name):
    if data_set_form.cleaned_data['is_created'] is True:
        name = data_set_form.data['name_created']

        def init_folders(data_set):
            data_set_dirpath = data_set.get_dirpath()  #, posted_file.name)
            os.makedirs(data_set_dirpath)

            for kind in ['reference', 'genes', 'operons']:
                posted_file = request.FILES.get(kind)
                if posted_file:
                    with open(os.path.join(data_set_dirpath, posted_file.name), 'wb+') as f:
                        for chunk in posted_file.chunks():
                            f.write(chunk)
                    setattr(data_set, kind + '_fname', posted_file.name)

        if name == '':
            data_set = DataSet(name=default_name, remember=False, user_session=user_session, user=user_session.user)
            data_set.save()
            init_folders(data_set)
            data_set.save()

        else:
            base_name = name
            i = 1
            while DataSet.objects.filter(name=name).exists():
                name = base_name + ' (' + str(i) + ')'
                i += 1

            data_set = DataSet(name=name, remember=True, user_session=user_session, user=user_session.user)
            data_set.save()
            init_folders(data_set)
            data_set.save()

    else:
        name = data_set_form.data['name_selected']
        if name == '' or name == 'no data set':
            data_set = None
        else:
            try:
                data_set = DataSet.objects.get(name=name)
            except DataSet.DoesNotExist:
                logger.error('Data set with name %s does not exits' % name)
                return HttpResponseBadRequest('Data set does not exist')

    return data_set


def start_quast_session(user_session, qs):
    # Preparing results directory
    # result_dirpath = qs.get_dirpath()

    #  if os.path.isdir(result_dirpath):
    #       i = 2
    #       base_dir_path = result_dirpath
    #       while os.path.isdir(result_dirpath):
    #           result_dirpath = base_dir_path + '_' + str(i)
    #           i += 1
    #  if not os.path.isdir(result_dirpath):
    #       os.makedirs(result_dirpath)

    # Preparing contigs files

    # contigs_files = filter(lambda cf: cf.fname in contigs_fnames, all_contigs_files)

    contigs_files = qs.contigs_files.all()
    logger.info('quast_app.views.index.POST: data set name = %s', str(contigs_files))

    #    for c_fn in contigs_files:
    #        QuastSession_ContigsFile.objects.create(quast_session=quast_session, contigs_file=c_fn)

    # evaluation_dirpath = qs.get_evaluation_contigs_dirpath()

    #    os.rename(quast_session.get_contigs_dirpath(), evaluation_dirpath)

    # os.makedirs(evaluation_dirpath)

    # evaluation_contigs_fpaths = [os.path.join(evaluation_dirpath, c_f.fname) for c_f in contigs_files]
    #    quast_session_contigs_fpaths = [os.path.join(contigs_results_tmp_dirpath, c_f.fname) for c_f in contigs_files]

    #    for user_c_fpath, quast_session_c_fpath in zip(user_contigs_fpaths, quast_session_contigs_fpaths):
    #        shutil.move(user_c_fpath, quast_session_c_fpath)

    #    for cf in contigs_files:
    #        cf.delete()

    #    for contigs_file in contigs_files:
    #        contigs_file.user_session

    contigs_dirpath = qs.get_contigs_dirpath()
    contigs_fpaths = [os.path.join(contigs_dirpath, c_f.fname) for c_f in contigs_files]

    # Preparing data set files
    data_set = qs.data_set

    reference_fpath = None
    genes_fpath = None
    operons_fpath = None
    if data_set:
        if data_set.reference_fname:
            reference_fpath = os.path.join(data_set.get_dirpath(), data_set.reference_fname)

        if data_set.genes_fname:
            genes_fpath = os.path.join(data_set.get_dirpath(), data_set.genes_fname)

        if data_set.operons_fname:
            operons_fpath = os.path.join(data_set.get_dirpath(), data_set.operons_fname)

    # Running Quast
    result = assess_with_quast(user_session, qs, contigs_fpaths,
                               reference_fpath, genes_fpath, operons_fpath)
    qs.task_id = result.id
    qs.save()
    return qs


def assess_with_quast(us, qs, contigs_paths,
                      reference_path=None, genes_path=None, operons_path=None):
    # contigs_files = qs.contigs_files.all()
    # contigs_paths = [os.path.join(quast_session.get_contigs_dirpath(), c_f.fname) for c_f in contigs_files]

    def quote(path):
        return '"' + path + '"'

    if len(contigs_paths) > 0:
        if os.path.isfile(settings.QUAST_PY_FPATH):
            args = [settings.QUAST_PY_FPATH] + map(quote, contigs_paths)
            if reference_path:
                args.append('-R')
                args.append(quote(reference_path))

            if genes_path:
                args.append('-G')
                args.append(quote(genes_path))

            if operons_path:
                args.append('-O')
                args.append(quote(operons_path))

            if qs.min_contig is not None:
                args.append('--min-contig')
                args.append(str(qs.min_contig))

            if qs.estimated_ref_size is not None:
                args.append('--est-ref-size')
                args.append(str(qs.estimated_ref_size))

            if qs.eukaryotic:
                args.append('--eukaryote')

            if qs.find_genes:
                args.append('--gene-finding')

            if qs.scaffolds:
                args.append('--scaffolds')

            res_dirpath = qs.get_dirpath()
            args.append('-J')
            args.append(quote(res_dirpath))

            args.append('-o')
            args.append(quote(os.path.join(res_dirpath, settings.REGULAR_REPORT_DIRNAME)))

            args.append('--err-fpath')
            args.append(os.path.join(res_dirpath, settings.ERROR_LOG_FNAME))

            args.append('-t')
            args.append('2')

            from tasks import start_quast
            # tasks.start_quast((args, quast_session))
            result = start_quast.delay((args, qs, us))

            return result
        else:
            if not os.path.isfile(settings.QUAST_PY_FPATH):
                raise Exception('quast_py_fpath ' + settings.QUAST_PY_FPATH + ' is not a file')
    else:
        raise Exception('no files with assemblies')
