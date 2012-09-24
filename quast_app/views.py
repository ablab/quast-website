import sys
import datetime
from celery.app.task import Task
from django.forms import forms
import os
import shutil
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest, Http404
from django.shortcuts import render_to_response, render, redirect
import tasks
from upload_backend import ContigsUploadBackend, ReferenceUploadBackend, GenesUploadBackend, OperonsUploadBackend
from django.conf import settings


glossary = '{}'
with open(os.path.join(settings.GLOSSARY_PATH)) as f:
    glossary = f.read()


def index(request):
    return render_to_response('index.html', {
        'glossary' : glossary,
    })


def manual(request):
    with open(settings.MANUAL_FPATH) as f:
        return HttpResponse(f.read())


def license(request):
    with open(settings.LICENSE_FPATH) as f:
        return HttpResponse(f.read(), content_type='text/plain')


def example(request):
    results_dirpath = os.path.join(settings.EXAMPLE_DIRPATH)
    response = response_with_report('example-report.html',
                                    results_dirpath,
                                    'E.coli',)
    return response


def report_scripts(request, script_name):
    with open(os.path.join(settings.REPORT_SCRIPTS_DIRPATH, script_name)) as f:
        return HttpResponse(f.read(), content_type='application/javascript')


from django.middleware.csrf import get_token
from django.template import RequestContext
from ajaxuploader.views import AjaxFileUploader
from models import UserSession, Dataset, QuastSession, ContigsFile, DatasetForm, QuastSession_ContigsFile

#if not request.session.exists(request.session.session_key):
#request.session.create()

def evaluate(request):
    if not request.session.exists(request.session.session_key):
        request.session.create()

    user_session_key = request.session.session_key
    try:
        user_session = UserSession.objects.get(session_key=user_session_key)
    except UserSession.DoesNotExist:
        user_session = create_user_session(user_session_key)

    contigs_fnames = [c_f.fname for c_f in user_session.contigsfile_set.all()]

    if request.method == 'POST':
        dataset_form = DatasetForm(request.POST)
        dataset_form.set_user_session(user_session)
#        dataset_form.fields['name_selected'].choices = dataset_choices
        if dataset_form.is_valid():
            from datetime import datetime
            now_datetime = datetime.now()
            now_str = now_datetime.strftime('%d_%b_%Y_%H:%M:%S.%f')

            dataset = get_dataset(request, dataset_form, now_str)
            quast_session = start_quast_session(user_session, dataset, now_datetime)

            return redirect('/reports/', after_evaluateion=True)

#            return render_to_response('reports.html', {
#                'glossary': glossary,
#                'csrf_token': get_token(request),
#                'session_key': user_session_key,
#                'contigs_fnames': contigs_fnames,
#                'dataset_form': dataset_form,
#                'report_id': quast_session.report_id,
#                }, context_instance = RequestContext(request))
    else:
        dataset_form = DatasetForm()
#        dataset_form.fields['name_selected'].choices = dataset_choices

    return render_to_response('evaluate.html', {
        'glossary': glossary,
        'csrf_token': get_token(request),
        'session_key': user_session_key,
        'contigs_fnames': contigs_fnames,
        'dataset_form': dataset_form,
        }, context_instance = RequestContext(request))


state_map = {
    'PENDING': 'PENDING',
    'STARTED': 'PENDING',
    'FAILURE': 'FAILURE',
    'SUCCESS': 'SUCCESS',
}


def reports(request, after_evaluation=False):
    if not request.session.exists(request.session.session_key):
        request.session.create()

    user_session_key = request.session.session_key
    try:
        user_session = UserSession.objects.get(session_key=user_session_key)
    except UserSession.DoesNotExist:
        user_session = create_user_session(user_session_key)


    quast_sessions_dicts = []
    quast_sessions = user_session.quastsession_set.all()
    if quast_sessions.exists():
        quast_sessions = sorted(quast_sessions, cmp=lambda qs1, qs2: 1 if qs1.date < qs2.date else -1)

        if after_evaluation:
            last = quast_sessions[0]
            result = tasks.start_quast.AsyncResult(last.task_id)
            if result and result.state == 'SUCCESS':
                return redirect('/report/', report_id=last.report_id)

        for qs in quast_sessions:
            result = tasks.start_quast.AsyncResult(qs.task_id)
            state = result.state
            state_repr = 'FAILURE'
            if result and state in state_map:
                state_repr = state_map[state]

            quast_session_dict = {
                'date': qs.date, #. strftime('%d %b %Y %H:%M:%S'),
                'report_link': '/report/' + qs.report_id,
                'with_dataset': True if qs.dataset else False,
                'dataset_name': qs.dataset.name if qs.dataset and qs.dataset.remember else '',
                'state': state_repr,
                'highlight_last': after_evaluation,
            }
            quast_sessions_dicts.append(quast_session_dict)

    return render_to_response('reports.html', {
        'glossary': glossary,
        'quast_sessions': quast_sessions_dicts,
    })



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


def get_dataset(request, dataset_form, now_str):
    if dataset_form.cleaned_data['created_or_selected'] == 'created':
        name = dataset_form.data['name_created']

        def init_folders(dataset):
            dataset_dirpath = os.path.join(settings.DATA_SETS_ROOT_DIRPATH, dataset.dirname) #, posted_file.name)
            os.makedirs(dataset_dirpath)

            for kind in ['reference', 'genes', 'operons']:
                posted_file = request.FILES.get(kind)
                if posted_file:
                    with open(os.path.join(dataset_dirpath, posted_file.name), 'wb+') as f:
                        for chunk in posted_file.chunks():
                            f.write(chunk)
                    setattr(dataset, kind + '_fname', posted_file.name)

        if name == '':
            dataset = Dataset(name=now_str, remember=False)
            dataset.save()
            init_folders(dataset)
            dataset.save()

        elif not Dataset.objects.filter(name=name).exists():
            dataset = Dataset(name=name, remember=True)
            dataset.save()
            init_folders(dataset)
            dataset.save()

        else:
            dataset = Dataset.objects.get(name=name)
            #TODO: invalidate

    else:
        name = dataset_form.data['name_selected']
        if name == 'no dataset':
            dataset = None
        else:
            try:
                dataset = Dataset.objects.get(name=name)
            except Dataset.DoesNotExist:
                return HttpResponseBadRequest('Dataset does not exist')

    return dataset


def report(request, report_id):
    user_session_key = request.session.session_key
    try:
        user_session = UserSession.objects.get(session_key=user_session_key)
    except UserSession.DoesNotExist:
        #TODO: invalidate
        return HttpResponseBadRequest('We do not recognize you.')


    if QuastSession.objects.filter(report_id=report_id).exists():
        if request.method == 'GET':
            quast_session = QuastSession.objects.get(report_id=report_id)
            result = tasks.start_quast.AsyncResult(quast_session.task_id)
            state = result.state

            if state == 'SUCCESS':
                header = 'Quality assessment'
                if quast_session.dataset and quast_session.dataset.remember:
                    header = quast_session.dataset.name

                return response_with_report(
                    'assess-report.html',
                    os.path.join(settings.RESULTS_ROOT_DIRPATH, quast_session.get_results_reldirpath()),
                    header,
                )
            else:
                state_repr = 'FAILURE'
                if result and state in state_map:
                    state_repr = state_map[state]

                return render_to_response('waiting-report.html', {
                    'glossary' : glossary,
                    'csrf_token': get_token(request),
                    'session_key' : request.session.session_key,
                    'state': state_repr,
                    'report_id': report_id,
                }, context_instance = RequestContext(request))

        if request.method == 'POST':
            #check status of quast session, return result
            pass

    else:
        if request.method == 'GET':
            raise Http404()

        if request.method == 'POST':
            pass



contigs_uploader = AjaxFileUploader(backend=ContigsUploadBackend)
#reference_uploader = AjaxFileUploader(backend=ReferenceUploadBackend)
#genes_uploader = AjaxFileUploader(backend=GenesUploadBackend)
#operons_uploader = AjaxFileUploader(backend=OperonsUploadBackend)


def start_quast_session(user_session, dataset, now_datetime):
    # Creating new Quast session object
    quast_session = QuastSession(
        user_session = user_session,
        dataset = dataset,
        date = now_datetime,
    )

    quast_session.save()

    for c_fn in user_session.contigsfile_set.all():
        QuastSession_ContigsFile.objects.create(quast_session=quast_session, contigs_file=c_fn)

    input_dirpath = os.path.join(settings.INPUT_ROOT_DIRPATH, user_session.input_dirname)

    # Preparing contigs filepaths
    print quast_session.get_results_reldirpath()
    contigs_files = quast_session.contigs_files.all()
    contigs_fpaths = [os.path.join(input_dirpath, c_f.fname) for c_f in contigs_files]

    # Preparing results directory
    result_dirpath = os.path.join(settings.RESULTS_ROOT_DIRPATH, quast_session.get_results_reldirpath())
    if os.path.isdir(result_dirpath):
        i = 2
        base_dir_path = result_dirpath
        while os.path.isdir(result_dirpath):
            result_dirpath = base_dir_path + '_' + str(i)
            i += 1
    if not os.path.isdir(result_dirpath):
        os.makedirs(result_dirpath)

    # Preparing dataset files
    reference_fpath = None
    genes_fpath = None
    operons_fpath = None
    if dataset:
        if dataset.reference_fname:
            reference_fpath = os.path.join(settings.DATA_SETS_ROOT_DIRPATH, dataset.dirname, dataset.reference_fname)

        if dataset.genes_fname:
            genes_fpath = os.path.join(settings.DATA_SETS_ROOT_DIRPATH, dataset.dirname, dataset.genes_fname)

        if dataset.operons_fname:
            operons_fpath = os.path.join(settings.DATA_SETS_ROOT_DIRPATH, dataset.dirname, dataset.operons_fname)

    # Running Quast
    result = assess_with_quast(result_dirpath, contigs_fpaths, reference_fpath, genes_fpath, operons_fpath)
    quast_session.task_id = result.id
    quast_session.save()
    return quast_session


def assess_with_quast(res_dirpath, contigs_paths, reference_path=None, genes_path=None, operons_path=None):
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

            args.append('-J')
            args.append(res_dirpath)

            # Draw no plots
            args.append('-p')

            args.append('-o')
            args.append(os.path.join(res_dirpath, 'regular_report'))

            from tasks import start_quast
            result = start_quast.delay(args)

            return result
        else:
            if not os.path.isfile(settings.QUAST_PY_FPATH):
                raise Exception('quast_py_fpath ' + settings.QUAST_PY_FPATH + ' is not a file')
    else:
        raise Exception('no files with assemblies')


def response_with_report(template, results_dirpath, header):
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

    report                  = get('report', is_required=True)
    contigs_lengths         = get('contigs_lengths', is_required=True)
    reference_length        = get('ref_length')
    assemblies_lengths      = get('assemblies_lengths')
    aligned_contigs_lengths = get('aligned_contigs_lengths')
    contigs                 = get('contigs')
    genes                   = get('genes')
    operons                 = get('operons')
    gc_info                 = get('gc')

    return render_to_response(template, {
            'glossary' : glossary,

            'report' : report,
            'contigsLenghts' : contigs_lengths,
            'alignedContigsLengths' : aligned_contigs_lengths,
            'assembliesLengths' : assemblies_lengths,
            'referenceLength' : reference_length,
            'contigs' : contigs,
            'genes' : genes,
            'operons' : operons,
            'gcInfo' : gc_info,

            'header' : header,
        }
    )


def ecoli(request):
    return response_with_report('ecoli.html', os.path.join(settings.ECOLI_DIRPATH), 'Ecoli')


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








