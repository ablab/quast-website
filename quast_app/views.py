import sys
import datetime
from celery.app.task import Task
from django.core.urlresolvers import reverse
from django.forms import forms
import os
import shutil
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, render, redirect
import tasks
from upload_backend import ContigsUploadBackend, ReferenceUploadBackend, GenesUploadBackend, OperonsUploadBackend
from django.conf import settings

import logging
logger = logging.getLogger('quast')

glossary = '{}'
with open(os.path.join(settings.GLOSSARY_PATH)) as f:
    glossary = f.read()


template_args_by_default = {
    'glossary': glossary,
    'google-analytics': settings.GOOGLE_ANALYTICS,
    'debug': settings.DEBUG,
}


def manual(request):
    with open(settings.MANUAL_FPATH) as f:
        return HttpResponse(f.read())


def license(request):
    with open(settings.LICENSE_FPATH) as f:
        return HttpResponse(f.read(), content_type='text/plain')


def example(request):
    example_dirpath = os.path.join(settings.EXAMPLE_DIRPATH)
    report_response_dict = get_report_response_dict(example_dirpath,
                                                    caption='Example',
                                                    comment='',
                                                    data_set_name='E.coli',
                                                    link='')
    response_dict = dict(report_response_dict.items() + template_args_by_default.items())
    return render_to_response('example-report.html', response_dict)


def benchmarking(request):
    return render_to_response('benchmarking.html', template_args_by_default)


def ecoli(request):
    json_dirpath = os.path.join(settings.ECOLI_DIRPATH)
    report_response_dict = get_report_response_dict(json_dirpath,
                                                    caption='SPAdes - IDBA collaboration',
                                                    comment='',
                                                    data_set_name='E.coli',
                                                    link='')
    response_dict = dict(report_response_dict.items() + template_args_by_default.items())
    return render_to_response('ecoli.html', response_dict)


#def report_scripts(request, script_name):
#    with open(os.path.join(settings.REPORT_SCRIPTS_DIRPATH, script_name)) as f:
#        return HttpResponse(f.read(), content_type='application/javascript')


from django.middleware.csrf import get_token
from django.template import RequestContext
from ajaxuploader.views import AjaxFileUploader
from models import UserSession, Dataset, QuastSession, slugify
from forms import DatasetForm

#if not request.session.exists(request.session.session_key):
#request.session.create()

if not settings.QUAST_DIRPATH in sys.path:
    sys.path.insert(1, settings.QUAST_DIRPATH)
from libs import qconfig


contigs_uploader = AjaxFileUploader(backend=ContigsUploadBackend)
#reference_uploader = AjaxFileUploader(backend=ReferenceUploadBackend)
#genes_uploader = AjaxFileUploader(backend=GenesUploadBackend)
#operons_uploader = AjaxFileUploader(backend=OperonsUploadBackend)


state_map = {
    'PENDING': 'PENDING',
    'STARTED': 'PENDING',
    'FAILURE': 'FAILURE',
    'SUCCESS': 'SUCCESS',
}


def index(request):
    logging.info('Somebody opened index')

    response_dict = template_args_by_default

    # User session
    if not request.session.exists(request.session.session_key):
        request.session.create()

    user_session_key = request.session.session_key
    try:
        user_session = UserSession.objects.get(session_key=user_session_key)
    except UserSession.DoesNotExist:
        user_session = create_user_session(user_session_key)
    response_dict['session_key'] = user_session_key

    # Evaluation
    if request.method == 'POST':
        data_set_form = DatasetForm(request.POST)
        data_set_form.set_user_session(user_session)

        report_id = data_set_form.data.get('report_id')
        if not report_id:
            logging.error('quast_app.views.index: data_set_form.data.get(\'report_id\') is None')
            return HttpResponseBadRequest('No report_id in form')
        try:
            quast_session = QuastSession.objects.get(report_id=report_id)
        except QuastSession.DoesNotExist:
            logging.error('quast_app.views.index: QuastSession with report_id=%s does not exist' % report_id)
            return HttpResponseBadRequest('No quast session with report_id=%s' % report_id)

        # Contigs fnames from this form
#        contigs_in_form = data_set_form.data.get('contigs')
#
#        split = contigs_in_form.split('\r\n')
#        if len(split) == 1:
#            split = contigs_in_form.split('\n')
#        if len(split) == 1:
#            logging.error('quast_app.views.index: No contigs fnames got from "data_set_form.contigs": the value got is %s', str(contigs_in_form))
#            return HttpResponseBadRequest("Error: no contigs loaded")

#        contigs_fnames = split[:-1]

        if data_set_form.is_valid():
            quast_session.submited = True

            min_contig = data_set_form.cleaned_data['min_contig']
            request.session['min_contig'] = min_contig
#            quast_session.min_contig = min_contig
            logging.info('quast_app.views.index.POST: min_contig = %d', min_contig)

            email = data_set_form.cleaned_data.get('email')
            if email:
                user_session.email = email
            logging.info('quast_app.views.index.POST: email = %s', email)

            quast_session.comment = data_set_form.cleaned_data.get('comment')

            caption = data_set_form.cleaned_data.get('caption')
            quast_session.caption = caption
            logging.info('quast_app.views.index.POST: caption = %s', caption)
            quast_session.generate_link()
            logging.info('quast_app.views.index.POST: link = %s', quast_session.link)

            data_set = get_data_set(request, data_set_form, default_name=quast_session.report_id)
            if data_set:
                request.session['default_data_set_name'] = data_set.name
                quast_session.dataset = data_set
                logging.info('quast_app.views.index.POST: data set name = %s', data_set.name)

            quast_session.save()

            # Starting Quast
            quast_session = start_quast_session(quast_session, min_contig)
            # return HttpResponseRedirect(reverse('quast_app.views.index', kwargs={'after_evaluation': True}))

            request.session['after_evaluation'] = True
            return redirect(index)
        else:
            logging.info('quast_app.views.index.POST: form invalid, errors are: = %s', str(data_set_form.errors.items()))


    elif request.method == 'GET':
        # Creating quast_session
        from django.utils import timezone
        date = timezone.now()
        report_id = date.strftime(QuastSession.get_report_id_format())

        while QuastSession.objects.filter(report_id=report_id).exists():
            date = timezone.now()
            report_id = date.strftime(QuastSession.get_report_id_format())

        quast_session = QuastSession(user_session=user_session,
                                     date=date,
                                     report_id=report_id,
                                     submited=False)

        quast_session.save()

        result_dirpath = quast_session.get_dirpath()
        if os.path.isdir(result_dirpath):
            logging.critical('QuastSession.__init__: results_dirpath "%s" already exists' % result_dirpath)
            return HttpResponseBadRequest()

        os.makedirs(result_dirpath)
        logging.info('QuastSession.__init__: created result dirpath: %s' % result_dirpath)

        os.makedirs(quast_session.get_contigs_dirpath())
        logging.info('QuastSession.__init__: created contigs dirpath: %s' % result_dirpath)

        quast_session.save()
        response_dict['report_id'] = quast_session.report_id

        # Initializing data set form
        data_set_form = DatasetForm()
        data_set_form.set_report_id(quast_session.report_id)

        min_contig = request.session.get('min_contig') or qconfig.min_contig
        data_set_form.set_min_contig(min_contig)

        data_set_form.set_email(user_session.email)

        default_data_set_name = request.session.get('default_data_set_name') or ''
        data_set_form.set_default_data_set_name(default_data_set_name)

    else:
        logging.warn('quast_app.views.index: Request method is %s' % request.method)
        return HttpResponseBadRequest("GET and POST are only supported here")


    # GET or not valid POST

    # uploaded_contigs_fnames = [c_f.fname for c_f in user_session.contigsfile_set.all()]

    response_dict = dict(response_dict.items() + {
        'csrf_token': get_token(request),
        'contigs_fnames': [],
        'dataset_form': data_set_form,
    }.items())


    # REPORTS
    reports_dict = get_reports_response_dict(
        user_session,
        after_evaluation=request.session.get('after_evaluation', False),
        limit=7)
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


#def get_evaluate_response_dict(request, user_session, url):
#    contigs_fnames = [c_f.fname for c_f in user_session.contigsfile_set.all()]
#
#    if request.method == 'POST':
#        data_set_form = DatasetForm(request.POST)
#        data_set_form.set_user_session(user_session)
#        #        dataset_form.fields['name_selected'].choices = dataset_choices
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
#        #                'dataset_form': dataset_form,
#        #                'report_id': quast_session.report_id,
#        #                }, context_instance = RequestContext(request))
#    else:
#        data_set_form = DatasetForm()
#        min_contig = request.session.get('min_contig') or qconfig.min_contig
#        data_set_form.set_min_contig(min_contig)
#
#    #        dataset_form.fields['name_selected'].choices = dataset_choices
#
#    response_dict = template_args_by_default
#    response_dict = dict(response_dict.items() + {
#        'csrf_token': get_token(request),
#        'contigs_fnames': contigs_fnames,
#        'dataset_form': data_set_form,
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



def get_reports_response_dict(user_session, after_evaluation=False, limit=None):
    quast_sessions_dict = []

    quast_sessions = user_session.quastsession_set.filter(submited=True).order_by('-date')
    if limit:
        quast_sessions = quast_sessions[:limit+1]

    show_more_link = False

    if quast_sessions.exists():
#        quast_sessions.sort(cmp=lambda qs1, qs2: 1 if qs1.date < qs2.date else -1)

#        if after_evaluation:
#            last = quast_sessions[0]
#            result = tasks.start_quast.AsyncResult(last.task_id)
#            if result and result.state == 'SUCCESS':
#                return redirect('/report/', report_id=last.report_id)

        for i, qs in enumerate(quast_sessions):
            if i == limit:
                show_more_link = True
            else:
                result = tasks.start_quast.AsyncResult(qs.task_id)
                state = result.state
                state_repr = 'FAILURE'
                if result and state in state_map:
                    state_repr = state_map[state]

                data_set = qs.dataset
                if data_set:
                    print str(data_set)

                quast_session_info = {
                    'date': qs.date, #. strftime('%d %b %Y %H:%M:%S'),
                    'report_link': settings.REPORT_LINK_BASE + (qs.link or qs.report_id),
                    'comment' : qs.comment,
                    'caption' : qs.caption,
                    'with_dataset': True if qs.dataset else False,
                    'dataset_name': qs.dataset.name if qs.dataset and qs.dataset.remember else '',
                    'state': state_repr,
                    'report_id': qs.report_id,
                }
                quast_sessions_dict.append(quast_session_info)

    return {
        'quast_sessions': quast_sessions_dict,
        'show_more_link': show_more_link,
        'highlight_last': after_evaluation,
        # 'highlight_last': True,
        'latest_report_link': quast_sessions_dict[0]['report_link'] if after_evaluation else None
    }


def reports(request, after_evaluation=False):
    if not request.session.exists(request.session.session_key):
        request.session.create()

    user_session_key = request.session.session_key
    try:
        user_session = UserSession.objects.get(session_key=user_session_key)
    except UserSession.DoesNotExist:
        user_session = create_user_session(user_session_key)

    response_dict = get_reports_response_dict(user_session, after_evaluation)
    return render_to_response('reports.html', response_dict)


def create_user_session(user_session_key):
    input_dirpath = os.path.join(settings.INPUT_ROOT_DIRPATH, user_session_key)
    if os.path.isdir(input_dirpath):
        shutil.rmtree(input_dirpath)
    os.makedirs(input_dirpath)

    user_session = UserSession(
        session_key = user_session_key,
        input_dirname = user_session_key,
        )
    user_session.save()
    return user_session



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
            data_set = Dataset(name=default_name, remember=False)
            data_set.save()
            init_folders(data_set)
            data_set.save()

        elif not Dataset.objects.filter(name=name).exists():
            data_set = Dataset(name=name, remember=True)
            data_set.save()
            init_folders(data_set)
            data_set.save()

        else:
            data_set = Dataset.objects.get(name=name)
            #TODO: invalidate

    else:
        name = data_set_form.data['name_selected']
        if name == '' or name == 'no data set':
            data_set = None
        else:
            try:
                data_set = Dataset.objects.get(name=name)
            except Dataset.DoesNotExist:
                logging.error('quast_app.views.get_data_set: name_created: Data set with name %s does not exits' % name)
                return HttpResponseBadRequest('Data set does not exist')

    return data_set


def report(request, link):
    if not request.session.exists(request.session.session_key):
        request.session.create()

#    user_session_key = request.session.session_key
#    try:
#        user_session = UserSession.objects.get(session_key=user_session_key)
#    except UserSession.DoesNotExist:
#        user_session = create_user_session(user_session_key)

    found = QuastSession.objects.filter(link=link)
    if not found.exists():
        found = QuastSession.objects.filter(report_id=link)

    if found.exists():
        if request.method == 'GET':
            quast_session = found[0]

            state = ''
            if quast_session.task_id == '1045104510450145' or quast_session.task_id == 1045104510450145: # if the celery tasks have lost but we sure that this evaluated successfully
                result = None
                state = 'SUCCESS'
            else:
                result = tasks.start_quast.AsyncResult(quast_session.task_id)
                state = result.state

            response_dict = template_args_by_default

            if state == 'SUCCESS':
                if quast_session.dataset and quast_session.dataset.remember:
                    data_set_name = quast_session.dataset.name
                else:
                    data_set_name = ''

                if data_set_name == '' and not quast_session.caption:
                    caption = 'Quality assessment'
                else:
                    caption = quast_session.caption

                response_dict = dict(response_dict.items() + get_report_response_dict(
                    os.path.join(settings.RESULTS_ROOT_DIRPATH, quast_session.get_reldirpath()),
                    caption,
                    quast_session.comment,
                    data_set_name,
                    link
                ).items())

                return render_to_response('assess-report.html', response_dict)

            else:
                state_repr = 'FAILURE'
                if result and state in state_map:
                    state_repr = state_map[state]

                response_dict = dict(response_dict.items() + {
                    'csrf_token': get_token(request),
                    'session_key' : request.session.session_key,
                    'state': state_repr,
                    'link': link,
                    'comment': quast_session.comment,
                    'caption': quast_session.caption,
                }.items())

                return render_to_response('waiting-report.html', response_dict, context_instance = RequestContext(request))

        if request.method == 'POST':
            #check status of quast session, return result
            raise Http404()

    else:
        raise Http404()


def download_report(request, link):
    if not request.session.exists(request.session.session_key):
        request.session.create()

    found = QuastSession.objects.filter(link=link)
    if not found.exists():
        found = QuastSession.objects.filter(report_id=link)

    if found.exists():
        quast_session = found[0]

        if quast_session.task_id == '1045104510450145' or\
           quast_session.task_id == 1045104510450145:
            # If the celery tasks have lost but we sure that this evaluated successfully
            # If the next time you need to restore tasks already evaluated but the database
            # is lost, put this task id to the quastsession record.
            state = 'SUCCESS'
        else:
            result = tasks.start_quast.AsyncResult(quast_session.task_id)
            state = result.state

        if state == 'SUCCESS':
            regular_report_path = os.path.join(quast_session.get_dirpath(),
                                               settings.REGULAR_REPORT_DIRNAME)
            old_regular_report_path = os.path.join(quast_session.get_dirpath(),
                                                   'regular_report')

            if not os.path.exists(regular_report_path):
                if os.path.exists(old_regular_report_path):
                    os.rename(old_regular_report_path, regular_report_path)
                else:
                    logging.warning('quast_app_download_report:'
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

            os.remove(settings.HTML_REPORT_FNAME)
            shutil.rmtree(settings.HTML_REPORT_AUX_DIRNAME)

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


def start_quast_session(quast_session, min_contig):
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
    logging.info('quast_app.views.index.POST: data set name = %s', str(contigs_files))

#    for c_fn in contigs_files:
#        QuastSession_ContigsFile.objects.create(quast_session=quast_session, contigs_file=c_fn)

    evaluation_dirpath = quast_session.get_evaluation_contigs_dirpath()

    os.rename(quast_session.get_contigs_dirpath(), evaluation_dirpath)

   # evaluation_dirpath = quast_session.get_evaluation_contigs_dirpath() # os.path.join(result_dirpath, settings.CONTIGS_DIRNAME)
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
    data_set = quast_session.dataset

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
    result = assess_with_quast(quast_session, evaluation_contigs_fpaths, min_contig, reference_fpath, genes_fpath, operons_fpath)
    quast_session.task_id = result.id
    quast_session.save()
    return quast_session


def assess_with_quast(quast_session, contigs_paths, min_contig, reference_path=None, genes_path=None, operons_path=None):
    contigs_files = quast_session.contigs_files.all()
#    contigs_paths = [os.path.join(quast_session.get_contigs_dirpath(), c_f.fname) for c_f in contigs_files]

    res_dirpath = quast_session.get_dirpath()
#    min_contig = quast_session.min_contig

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
            result = start_quast.delay((args, quast_session))

            return result
        else:
            if not os.path.isfile(settings.QUAST_PY_FPATH):
                raise Exception('quast_py_fpath ' + settings.QUAST_PY_FPATH + ' is not a file')
    else:
        raise Exception('no files with assemblies')


def get_report_response_dict(results_dirpath, caption, comment, data_set_name, link):
    if dir is None:
        raise Exception('No results directory.')

    def get(name, is_required=False, msg=None):
        contents = ''
        try:
            f = open(os.path.join(results_dirpath, name + '.json'))
            contents = f.read()
        except IOError:
            if is_required:
                raise Exception(name + ' is not found but required.')
        return contents

    try:
        total_report = get('total_report', is_required=True)
    except Exception, e:
        total_report = get('report', is_required=True)

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
        data_set_name = data_set_name
    else:
        header = data_set_name
        data_set_name = ''

    return {
        'totalReport' : total_report,
        'contigsLenghts' : contigs_lengths,
        'alignedContigsLengths' : aligned_contigs_lengths,
        'assembliesLengths' : assemblies_lengths,
        'referenceLength' : reference_length,
        'genesInContigs' : genes_in_contigs,
        'operonsInContigs' : operons_in_contigs,
        'gcInfo' : gc_info,

        'header' : header,
        'data_set_name' : data_set_name,
        'comment' : comment,
        'link': link,

#        'qualities': quality_dict,
#        'mainMetrics': main_metrics,
    }


#static_path = 'app/static/'
#
#def get_static_file(request, path):
#    try:
#        contents = open(static_path + path)
#    except IOError:
#        return ''
#    else:
#        return HttpResponse(contents)


#def tar_archive(request, version):
#    path = '/Users/vladsaveliev/Dropbox/bio/quast/quast_website/quast' + version + '.tar.gz'
#
#    if os.path.isfile(path):
#        response = HttpResponse(mimetype='application/x-gzip')
#        response['Content-Disposition'] = 'attachment; filename=quast' + version +'.tar.gz'
#        response['X-Sendfile'] = path
#        return response
#    else:
#        raise Http404
