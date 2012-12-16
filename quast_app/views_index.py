import sys
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


def index_view(user_session, response_dict, request):
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
        mailer.info(log_msg)

        data_set_form = DataSetForm(request.POST)
        data_set_form.set_user_session(user_session)

        report_id = data_set_form.data.get('report_id')
        if not report_id:
            logger.error('data_set_form.data.get(\'report_id\') is None')
            return HttpResponseBadRequest('No report_id in form')

        try:
            quast_session = QuastSession.objects.get(report_id=report_id)
        except QuastSession.DoesNotExist:
            logger.error('QuastSession with report_id=%s does not exist' % report_id)
            return HttpResponseBadRequest('No quast session with report_id=%s' % report_id)

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

        if data_set_form.is_valid():
            quast_session.submitted = True

            min_contig = data_set_form.cleaned_data['min_contig']
            request.session['min_contig'] = min_contig
            quast_session.min_contig = min_contig
            logger.info('quast_app.views.index.POST: min_contig = %d', min_contig)

            # email = data_set_form.cleaned_data.get('email')
            # if email:
            #     user_session.email = email
            # logger.info('quast_app.views.index.POST: email = %s', email)

            quast_session.comment = data_set_form.cleaned_data.get('comment')

            caption = data_set_form.cleaned_data.get('caption')
            quast_session.caption = caption
            logger.info('quast_app.views.index.POST: caption = %s', caption)
            quast_session.generate_link()
            logger.info('quast_app.views.index.POST: link = %s', quast_session.link)

            data_set = get_data_set(request, data_set_form, default_name=quast_session.report_id)
            if data_set:
                user_session.set_default_data_set(data_set)
                quast_session.data_set = data_set
                logger.info('quast_app.views.index.POST: data set name = %s', data_set.name)

            quast_session.save()

            # Starting Quast
            quast_session = start_quast_session(user_session, quast_session, min_contig)
            # return HttpResponseRedirect(reverse('True}))

            request.session['after_evaluation'] = True
            return redirect('quast_app.views.index')

#            return redirect('quast_app.views.report', link=quast_session.link)
        else:
            logger.info('quast_app.views.index.POST: form invalid, errors are: = %s', str(data_set_form.errors.items()))


    elif request.method == 'GET':
        # Creating quast_session
        quast_session = QuastSession.create(user_session)
        response_dict['report_id'] = quast_session.report_id

        # Initializing data set form
        data_set_form = DataSetForm()
        data_set_form.set_report_id(quast_session.report_id)

        if not settings.QUAST_DIRPATH in sys.path:
            sys.path.insert(1, settings.QUAST_DIRPATH)
        from libs import qconfig
        min_contig = request.session.get('min_contig') or qconfig.min_contig
        data_set_form.set_min_contig(min_contig)
        # data_set_form.set_email(user_session.email)

        # Default data set for this user
        if user_session.get_default_data_set():
            default_data_set_name = user_session.get_default_data_set().name
        else:
            default_data_set_name = request.session.get('default_data_set_name') or ''
            if default_data_set_name:
                try:
                    default_data_set = DataSet.objects.get(name=default_data_set_name)
                    user_session.set_default_data_set(default_data_set)
                except DataSet.DoesNotExist:
                    pass

        data_set_form.set_default_data_set_name(default_data_set_name)

    else:
        logger.warn('Request method is %s' % request.method)
        return HttpResponseBadRequest("GET and POST are only supported here")


    # uploaded_contigs_fnames = [c_f.fname for c_f in user_session.contigsfile_set.all()]

    response_dict = dict(response_dict.items() + {
        'csrf_token': get_token(request),
        'contigs_fnames': [],
        'data_set_form': data_set_form,
        'email': user_session.get_email(),
        'session_key': user_session.session_key,
        'is_authorized': user_session.user is not None,
    }.items())


    # REPORTS
    reports_dict = get_reports_response_dict(
        user_session,
        after_evaluation=request.session.get('after_evaluation', False),
        limit=settings.REPORTS_SHOW_LIMIT)
    response_dict = dict(response_dict.items() + reports_dict.items())
    request.session['after_evaluation'] = False


    # EXAMPLE
    example_dirpath = os.path.join(settings.EXAMPLE_DIRPATH)
    example_dict = get_report_response_dict(example_dirpath,
                                            caption='Example',
                                            comment='',
                                            data_set_name='E.coli',
                                            link='')
    response_dict = dict(response_dict.items() + example_dict.items())

    return render_to_response(
        'index.html',
        response_dict,
        context_instance = RequestContext(request)
    )


def get_data_set(request, data_set_form, default_name):
    if data_set_form.cleaned_data['is_created'] == True:
        name = data_set_form.data['name_created']

        def init_folders(data_set):
            data_set_dirpath = data_set.get_dirpath() #, posted_file.name)
            os.makedirs(data_set_dirpath)

            for kind in ['reference', 'genes', 'operons']:
                posted_file = request.FILES.get(kind)
                if posted_file:
                    with open(os.path.join(data_set_dirpath, posted_file.name), 'wb+') as f:
                        for chunk in posted_file.chunks():
                            f.write(chunk)
                    setattr(data_set, kind + '_fname', posted_file.name)

        if name == '':
            data_set = DataSet(name=default_name, remember=False)
            data_set.save()
            init_folders(data_set)
            data_set.save()

        elif not DataSet.objects.filter(name=name).exists():
            data_set = DataSet(name=name, remember=True)
            data_set.save()
            init_folders(data_set)
            data_set.save()

        else:
            data_set = DataSet.objects.get(name=name)
            #TODO: invalidate

    else:
        name = data_set_form.data['name_selected']
        if name == '' or name == 'no data set':
            data_set = None
        else:
            try:
                data_set = DataSet.objects.get(name=name)
            except DataSet.DoesNotExist:
                logger.error('name_created: Data set with name %s does not exits' % name)
                return HttpResponseBadRequest('Data set does not exist')

    return data_set


def start_quast_session(user_session, quast_session, min_contig):
    # Preparing results directory
    result_dirpath = quast_session.get_dirpath()

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

    contigs_files = quast_session.contigs_files.all()
    logger.info('quast_app.views.index.POST: data set name = %s', str(contigs_files))

    #    for c_fn in contigs_files:
    #        QuastSession_ContigsFile.objects.create(quast_session=quast_session, contigs_file=c_fn)

    evaluation_dirpath = quast_session.get_evaluation_contigs_dirpath()

#    os.rename(quast_session.get_contigs_dirpath(), evaluation_dirpath)

    # os.makedirs(evaluation_dirpath)

    evaluation_contigs_fpaths = [os.path.join(evaluation_dirpath, c_f.fname) for c_f in contigs_files]
    #    quast_session_contigs_fpaths = [os.path.join(contigs_results_tmp_dirpath, c_f.fname) for c_f in contigs_files]

    #    for user_c_fpath, quast_session_c_fpath in zip(user_contigs_fpaths, quast_session_contigs_fpaths):
    #        shutil.move(user_c_fpath, quast_session_c_fpath)

    #    for cf in contigs_files:
    #        cf.delete()


    #    for contigs_file in contigs_files:
    #        contigs_file.user_session

    # Preparing data set files
    data_set = quast_session.data_set

    reference_fpath = None
    genes_fpath = None
    operons_fpath = None
    if data_set:
        if data_set.reference_fname:
            reference_fpath = os.path.join(settings.DATA_SETS_ROOT_DIRPATH, data_set.dirname, data_set.reference_fname)

        if data_set.genes_fname:
            genes_fpath = os.path.join(settings.DATA_SETS_ROOT_DIRPATH, data_set.dirname, data_set.genes_fname)

        if data_set.operons_fname:
            operons_fpath = os.path.join(settings.DATA_SETS_ROOT_DIRPATH, data_set.dirname, data_set.operons_fname)

    # Running Quast
    result = assess_with_quast(user_session, quast_session, evaluation_contigs_fpaths, min_contig, reference_fpath, genes_fpath, operons_fpath)
    quast_session.task_id = result.id
    quast_session.save()
    return quast_session


def assess_with_quast(user_session, quast_session, contigs_paths, min_contig,
                      reference_path=None, genes_path=None, operons_path=None):
    contigs_files = quast_session.contigs_files.all()
    # contigs_paths = [os.path.join(quast_session.get_contigs_dirpath(), c_f.fname) for c_f in contigs_files]

    res_dirpath = quast_session.get_dirpath()
    # min_contig = quast_session.min_contig

    if len(contigs_paths) > 0:
        if os.path.isfile(settings.QUAST_PY_FPATH):
            args = [settings.QUAST_PY_FPATH] + contigs_paths
            if reference_path:
                args.append('-R')
                args.append(reference_path)

            if genes_path:
                args.append('-G')
                args.append(genes_path)

            if operons_path:
                args.append('-O')
                args.append(operons_path)

            if min_contig:
                args.append('--min-contig')
                args.append(str(min_contig))

            args.append('-J')
            args.append(res_dirpath)

            args.append('-o')
            args.append(os.path.join(res_dirpath, settings.REGULAR_REPORT_DIRNAME))

            from tasks import start_quast
            #            tasks.start_quast((args, quast_session))
            result = start_quast.delay((args, quast_session, user_session))

            return result
        else:
            if not os.path.isfile(settings.QUAST_PY_FPATH):
                raise Exception('quast_py_fpath ' + settings.QUAST_PY_FPATH + ' is not a file')
    else:
        raise Exception('no files with assemblies')
