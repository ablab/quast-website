import sys
from celery.app.task import Task
import os
import shutil
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest, Http404
from django.shortcuts import render_to_response, render
from quast_app import tasks
from quast_app.upload_backend import ContigsUploadBackend, ReferenceUploadBackend, GenesUploadBackend, OperonsUploadBackend
from quast_website import settings


glossary = '{}'
with open(os.path.join(settings.static_dirpath, 'glossary.json')) as f:
    glossary = f.read()


def index(request):
    return render_to_response('index.html', {
        'glossary' : glossary,
    })


def manual(request):
    with open(os.path.join(settings.static_dirpath, 'manual.html')) as f:
        return HttpResponse(f.read())


def license(request):
    with open(os.path.join(settings.static_dirpath, 'LICENSE')) as f:
        return HttpResponse(f.read(), content_type='text/plain')


def latest(request):
    path = os.path.join(settings.home_dirpath, 'latest_results/')
    response = response_with_report('latest-report.html', path)
    return response


#def assess_upload_with_quast(upload_dirpath, res_dirpath):
#    if os.path.isdir(upload_dirpath):
#        contigs_dirpath = os.path.join(upload_dirpath, 'contigs')
#        reference_dirpath = os.path.join(upload_dirpath, 'reference')
#        genes_dirpath = os.path.join(upload_dirpath, 'genes')
#        operons_dirpath = os.path.join(upload_dirpath, 'operons')
#
#        contigs_fpaths = []
#
#        if not os.path.isdir(contigs_dirpath):
#            raise Exception('adp_contigs_path ' + contigs_dirpath + ' is not dir')
#        else:
#            for fn in os.listdir(contigs_dirpath):
#                fpath = os.path.join(contigs_dirpath, fn)
#                if os.path.isfile(fpath):
#                    contigs_fpaths.append(fpath)
#
#        if not os.path.isdir(reference_dirpath) or os.listdir(reference_dirpath) == 0:
#            reference_fpath = None
#        else:
#            reference_fpath = os.path.join(reference_dirpath, os.listdir(reference_dirpath)[0])
#
#        if not os.path.isdir(genes_dirpath) or os.listdir(genes_dirpath) == 0:
#            genes_fpath = None
#        else:
#            genes_fpath = os.path.join(genes_dirpath, os.listdir(genes_dirpath)[0])
#
#        if not os.path.isdir(operons_dirpath) or os.listdir(operons_dirpath) == 0:
#            operons_fpath = None
#        else:
#            operons_fpath = os.path.join(operons_dirpath, os.listdir(operons_dirpath)[0])
#
#        return assess_with_quast(res_dirpath, contigs_fpaths, reference_fpath, genes_fpath, operons_fpath)



#class UploadAssemblyForm(forms.Form):
#    contigs     = forms.FileField()
#    reference   = forms.FileField(required=False)
#    genes       = forms.FileField(required=False)
#    operons     = forms.FileField(required=False)


#
#def create_unique_dir(dir_name):
#    dir_path = settings.home_dirpath + dir_name + '_' + datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
#
#    if os.path.isdir(dir_path):
#        i = 2
#        base_dir_path = dir_path
#        while os.path.isdir(dir_path):
#            dir_path = base_dir_path + '_' + str(i)
#            i += 1
#
#    if not os.path.isdir(dir_path):
#        os.makedirs(dir_path)
#
#    return os.path.abspath(dir_path)


#def handle_uploaded_file(dir_path, f):
#    fn = os.path.join(dir_path, f.name)
#
#    with open(fn, 'wb+') as destination:
#        for chunk in f.chunks():
#            destination.write(chunk)
#    return fn


# request.FILES is a dictionary of UploadedFile objects, where files are contigs,
# and optionally a reference, genes and operons.
#def assess(request):
#    contigs_path = reference_path = operons_path = genes_path = None
#
#    if request.method == 'POST':
#        form = UploadAssemblyForm(request.POST, request.FILES, label_suffix='')
#
#        if form.is_valid():
#            data_dir_path = create_unique_dir('input/input')
#
#            contigs = request.FILES.get('contigs')
#            if contigs:
#                contigs_path = handle_uploaded_file(data_dir_path, contigs)
#
#            reference = request.FILES.get('reference')
#            if reference:
#                reference_path = handle_uploaded_file(data_dir_path, reference)
#
#            genes = request.FILES.get('genes')
#            if genes:
#                genes_path = handle_uploaded_file(data_dir_path, genes)
#
#            operons = request.FILES.get('operons')
#            if operons:
#                operons_path = handle_uploaded_file(data_dir_path, operons)
#
#            results_dir = assess_with_quast(contigs_path, reference_path, genes_path, operons_path)
#            return response_with_report('assess-report.html', results_dir)
#
#    else:
#        form = UploadAssemblyForm(label_suffix='')
#
#    return render(request, 'assess.html', {'form' : form })


from django.middleware.csrf import get_token
from django.template import RequestContext
from ajaxuploader.views import AjaxFileUploader
from quast_app.models import UserSession, Dataset, QuastSession, ContigsFileName, DatasetForm, QuastSession_ContigsFileName


def evaluate(request):
    user_session_key = request.session.session_key
    try:
        user_session = UserSession.objects.get(session_key=user_session_key)
    except UserSession.DoesNotExist:
        user_session = create_user_session(user_session_key)

    contigs_fnames = [cfname.fname for cfname in user_session.contigsfilename_set.all()]

    if request.method == 'POST':
        dataset_form = DatasetForm(request.POST)
#        dataset_form.fields['name_selected'].choices = dataset_choices
        if dataset_form.is_valid():
            if not user_session.contigsfilename_set:
                return HttpResponseBadRequest('No contigs provided')
                #TODO: join this validation with form validation.

            dataset = get_dataset(request, dataset_form)
            quast_session = start_quast_session(user_session, dataset)

            return render_to_response('evaluate.html', {
                'glossary': glossary,
                'csrf_token': get_token(request),
                'session_key': user_session_key,
                'contigs_fnames': contigs_fnames,
                'dataset_form': dataset_form,
                'report_id': quast_session.report_id,
                }, context_instance = RequestContext(request))
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


def create_user_session(user_session_key):
    input_dirpath = os.path.join(settings.input_root_dirpath, user_session_key)
    if os.path.isdir(input_dirpath):
        shutil.rmtree(input_dirpath)
    os.makedirs(input_dirpath)

    user_session = UserSession(
        session_key = user_session_key,
        input_dirname = user_session_key,
        )
    user_session.save()
    return user_session


def get_dataset(request, dataset_form):
    if dataset_form.cleaned_data['created_or_selected'] == 'created':
        name = dataset_form.data['name_created']
        if Dataset.objects.filter(name=name).exists():
            return HttpResponseBadRequest('Dataset already exists')
            #TODO: invalidate
        else:
            dataset = Dataset(name=name)

            for kind in ['reference', 'genes', 'operons']:
                posted_file = request.FILES.get(kind)
                if posted_file:
                    with open(os.path.join(dataset.dirname, posted_file.name), 'wb+') as f:
                        for chunk in f.chunks():
                            f.write(chunk)
                    setattr(dataset, kind + '_fname', posted_file.name)
    else:
        name = dataset_form.data['name_selected']
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

            print result.state
            print result.id
            print quast_session.task_id
            if result.ready():
#                print 'Quast stdout:'
#                print result.stdout
#                print 'Quast stderr:'
#                print result.stderr
                return response_with_report(
                    'assess-report.html',
                    os.path.join(settings.results_root_dirpath, quast_session.get_results_reldirpath())
                )

            else:
                return render_to_response('waiting-report.html', {
                    'glossary' : glossary,
                    'csrf_token': get_token(request),
                    'session_key' : request.session.session_key,
                    'state': result.state,
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


def start_quast_session(user_session, dataset):
    # Creating new Quast session object
    quast_session = QuastSession(
        user_session = user_session,
        dataset = dataset
    )
    quast_session.save()

    for c_fn in user_session.contigsfilename_set.all():
        QuastSession_ContigsFileName.objects.create(quast_session=quast_session, contigs_filename=c_fn)

    input_dirpath = os.path.join(settings.input_root_dirpath, user_session.input_dirname)


    # Preparing contigs filepaths
    print quast_session.get_results_reldirpath()
    contigs_fnames = quast_session.contigs_filenames.all()
    contigs_fpaths = [os.path.join(input_dirpath, 'contigs', c_fn.fname) for c_fn in contigs_fnames]

    # Preparing results directory
    result_dirpath = os.path.join(settings.results_root_dirpath, quast_session.get_results_reldirpath())
    if os.path.isdir(result_dirpath):
        i = 2
        base_dir_path = result_dirpath
        while os.path.isdir(result_dirpath):
            result_dirpath = base_dir_path + '_' + str(i)
            i += 1
    if not os.path.isdir(result_dirpath):
        os.makedirs(result_dirpath)
    # Preparing dataset files
    dataset = quast_session.dataset
    reference_fpath = None
    genes_fpath = None
    operons_fpath = None
    if dataset:
        if dataset.reference_fname:
            reference_fpath = os.path.join(settings.datasets_root_dirpath, dataset.dirname, dataset.reference_fname)

        if dataset.genes_fname:
            genes_fpath = os.path.join(settings.datasets_root_dirpath, dataset.dirname, dataset.genes_fname)

        if dataset.operons_fname:
            operons_fpath = os.path.join(settings.datasets_root_dirpath, dataset.dirname, dataset.operons_fname)

    # Running Quast
    result = assess_with_quast(result_dirpath, contigs_fpaths, reference_fpath, genes_fpath, operons_fpath)
    quast_session.task_id = result.id
    quast_session.save()
    return quast_session


def assess_with_quast(res_dirpath, contigs_paths, reference_path=None, genes_path=None, operons_path=None):
    if len(contigs_paths) > 0:
        if os.path.isfile(settings.quast_py_path):
          # old_dir = os.getcwd()
          # os.chdir(settings.quast_path)

            args = [settings.quast_py_path] + contigs_paths
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

            from tasks import start_quast
            result = start_quast.delay(args)

          # os.chdir(old_dir)
            return result
        else:
            if not os.path.isfile(settings.quast_py_path):
                raise Exception('quast_py_path ' + settings.quast_py_path + ' is not file')
    else:
        raise Exception('it has to be a least one contigs file')


def response_with_report(template, dir):
    if dir is None:
        raise Exception('No results directory.')

    def get(name, is_required=False, msg=None):
        contents = ''
        try:
            f = open(os.path.join(dir, name + '.json'))
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
        }
    )


#static_path = 'quast_app/static/'
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








