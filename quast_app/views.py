import os


development = True
static_dirpath = 'static/'
home_dirpath = ''
quast_path = os.path.abspath('../quast/')


import subprocess
import datetime
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render_to_response, render
from django import forms
from quast_app.upload_backend import ContigsUploadBackend, ReferenceUploadBackend, GenesUploadBackend, OperonsUploadBackend



glossary = '{}'
with open(os.path.join(static_dirpath, 'glossary.json')) as f:
    glossary = f.read()


def index(request):
    return render_to_response('index.html', {
        'glossary' : glossary,
        })


def manual(request):
    with open(os.path.join(static_dirpath, 'manual.html')) as f:
        return HttpResponse(f.read())


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
    })


def latest(request):
    path = os.path.join(home_dirpath, 'latest_results/')
    response = response_with_report('latest-report.html', path)
    return response


quast_py_path = os.path.join(quast_path, 'quast.py')


def assess_upload_with_quast(adp_upload_path):
    if os.path.isdir(adp_upload_path):
        adp_contigs_path = os.path.join(adp_upload_path, 'contigs')
        adp_reference_path = os.path.join(adp_upload_path, 'reference')
        adp_genes_path = os.path.join(adp_upload_path, 'genes')
        adp_operons_path = os.path.join(adp_upload_path, 'operons')

        afps_contigs = []

        if not os.path.isdir(adp_contigs_path):
            raise Exception('adp_contigs_path ' + adp_contigs_path + ' is not dir')
        else:
            for fn_file in os.listdir(adp_contigs_path):
                afp_file = os.path.join(adp_contigs_path, fn_file)
                if os.path.isfile(afp_file):
                    afps_contigs.append(afp_file)

        if not os.path.isdir(adp_reference_path) or os.listdir(adp_reference_path) == 0:
            afp_reference_path = None
        else:
            afp_reference_path = os.path.join(adp_reference_path, os.listdir(adp_reference_path)[0])

        if not os.path.isdir(adp_genes_path) or os.listdir(adp_genes_path) == 0:
            afp_genes_path = None
        else:
            afp_genes_path = os.path.join(adp_genes_path, os.listdir(adp_genes_path)[0])

        if not os.path.isdir(adp_operons_path) or os.listdir(adp_operons_path) == 0:
            afp_operons_path = None
        else:
            afp_operons_path = os.path.join(adp_operons_path, os.listdir(adp_operons_path)[0])

        return assess_with_quast(afps_contigs, afp_reference_path, afp_genes_path, afp_operons_path)


def assess_with_quast(contigs_paths, reference_path=None, genes_path=None, operons_path=None):
    if len(contigs_paths) > 0:
        if os.path.isfile(quast_py_path):
            result_path = create_unique_dir('results/results')

            old_dir = os.getcwd()
            os.chdir(quast_path)

            args = [quast_py_path] + contigs_paths
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
            args.append(result_path)

            from celery_start_quast import start_quast
            start_quast(args)

#            out = ''
#            err = ''
#            try:
#                proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#                while True:
#                    line = proc.stderr.readline()
#                    if line != '':
#                        out = out + 'Quast err ' + line + '\n'
#                    else:
#                        break
#                proc.wait()
#
#            except Exception as e:
#                raise Exception(out + err + '\n' + e.strerror)

            os.chdir(old_dir)
            return result_path

        else:
            if not os.path.isfile(quast_py_path):
                raise Exception('quast_py_path ' + quast_py_path + ' is not file')
            else:
                raise Exception('quast_py_path ' + quast_py_path + ' is a file')

    else:
        raise Exception('it has to be a least one contigs file')


class UploadAssemblyForm(forms.Form):
    contigs     = forms.FileField()
    reference   = forms.FileField(required=False)
    genes       = forms.FileField(required=False)
    operons     = forms.FileField(required=False)


def create_unique_dir(dir_name):
    dir_path = home_dirpath + dir_name + '_' + datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')

    if os.path.isdir(dir_path):
        i = 2
        base_dir_path = dir_path
        while os.path.isdir(dir_path):
            dir_path = base_dir_path + '_' + str(i)
            i += 1

    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)

    return os.path.abspath(dir_path)


def handle_uploaded_file(dir_path, f):
    fn = os.path.join(dir_path, f.name)

    with open(fn, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return fn


# request.FILES is a dictionary of UploadedFile objects, where files are contigs,
# and optionally a reference, genes and operons.
def assess(request):
    contigs_path = reference_path = operons_path = genes_path = None

    if request.method == 'POST':
        form = UploadAssemblyForm(request.POST, request.FILES, label_suffix='')

        if form.is_valid():
            data_dir_path = create_unique_dir('input')

            contigs = request.FILES.get('contigs')
            if contigs:
                contigs_path = handle_uploaded_file(data_dir_path, contigs)

            reference = request.FILES.get('reference')
            if reference:
                reference_path = handle_uploaded_file(data_dir_path, reference)

            genes = request.FILES.get('genes')
            if genes:
                genes_path = handle_uploaded_file(data_dir_path, genes)

            operons = request.FILES.get('operons')
            if operons:
                operons_path = handle_uploaded_file(data_dir_path, operons)

            results_dir = assess_with_quast(contigs_path, reference_path, genes_path, operons_path)
            return response_with_report('assess-report.html', results_dir)

    else:
        form = UploadAssemblyForm(label_suffix='')

    return render(request, 'assess.html', {'form' : form })


from django.middleware.csrf import get_token
from django.template import RequestContext
from ajaxuploader.views import AjaxFileUploader

def evaluate(request):
    request.session['upload_directory'] = create_unique_dir('input/input')

    return render_to_response('evaluate.html', {
        'glossary' : glossary,
        'csrf_token': get_token(request),
        'session_id' : request.session.get
    }, context_instance = RequestContext(request))


contigs_uploader = AjaxFileUploader(backend_class=ContigsUploadBackend)
reference_uploader = AjaxFileUploader(backend_class=ReferenceUploadBackend)
genes_uploader = AjaxFileUploader(backend_class=GenesUploadBackend)
operons_uploader = AjaxFileUploader(backend_class=OperonsUploadBackend)


def evaluate_get_report(request):
    adp_upload_dir = request.session.get('upload_directory')

    if adp_upload_dir:
        results_dir = assess_upload_with_quast(adp_upload_dir)
        return response_with_report('assess-report.html', results_dir)


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











