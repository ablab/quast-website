import os
import subprocess
import datetime
from django.http import Http404, HttpResponse
from django.shortcuts import render_to_response, render
from django import forms

glossary_path = 'static/glossary.json'


def index(request):
    glossary = open(glossary_path).read()
    return render_to_response('index.html', {
        'glossary' : glossary,
    })


def manual(request):
    contents = open('static/manual.html').read()
    return HttpResponse(contents)


def response_with_report(template, dir):
    glossary = open(glossary_path).read()

    def get(name, is_required=False, msg=None):
        try:
            return open(os.path.join(dir, name + '.json')).read()
        except IOError:
            if is_required:
                raise Http404(msg)
            return None

    report                  = get('report', is_required=True)
    contigs_lengths         = get('contigs_lengths', is_required=True)
    reference_length        = get('ref_length')
    assemblies_lengths      = get('assemblies_lengths')
    aligned_contigs_lengths = get('aligned_contigs_lengths')
    contigs                 = get('contigs')
    genes                   = get('genes')
    operons                 = get('operons')

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
    })


def latestreport(request):
    return response_with_report('latest-report.html', 'quast_results_archive_json/latest/')


quast_path = os.path.abspath('../quast/')
quast_py_path = os.path.join(quast_path, 'quast.py')


def assess_with_quast(contigs_path, reference_path, genes_path, operons_path):
    if contigs_path:
        if os.path.isfile(quast_py_path):
            result_path = create_unique_dir('results')

            os.chdir(quast_path)

            args = [quast_py_path, contigs_path]
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

            proc = subprocess.Popen(args, stdout=subprocess.PIPE)
            while True:
                line = proc.stdout.readline()
                if line != '':
                    print 'Quast: ', line,
                else:
                    break
            proc.wait()

            os.chdir('../quast-website')

            return result_path

    raise Http404


class UploadAssemblyForm(forms.Form):
    contigs     = forms.FileField()
    reference   = forms.FileField(required=False)
    genes       = forms.FileField(required=False)
    operons     = forms.FileField(required=False)


def create_unique_dir(dir_name):
    dir_name = dir_name + '_' + datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')

    if os.path.isdir(dir_name):
        i = 2
        base_dir_name = dir_name
        while os.path.isdir(dir_name):
            dir_name = base_dir_name + '_' + str(i)
            i += 1

    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)

    return os.path.abspath(dir_name)


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
            raise Http404

    else:
        form = UploadAssemblyForm(label_suffix='')

    return render(request, 'assess.html', {'form' : form })









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








