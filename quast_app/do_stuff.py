from django.shortcuts import render_to_response
import os
from quast_app.models import Dataset
from quast_website import settings

glossary = '{}'
with open(os.path.join(settings.static_dirpath, 'glossary.json')) as f:
    glossary = f.read()

def do_stuff(request):
    dataset = Dataset(
        name = 'E. coli, first 10K',
        genes_fname = 'genes_10K.gff',
        operons_fname = 'operons_10K.gff',
        reference_fname = 'reference_10K.fasta.gz',
        dirname = 'e-coli-10k',
    )
    dataset.save()

    dataset = Dataset(
        name = 'E. coli',
        genes_fname = 'genes.gff',
        operons_fname = 'operons.gff',
        reference_fname = 'reference.fasta.gz',
        dirname = 'e-coli',
    )
    dataset.save()

    return render_to_response('index.html', {
            'glossary' : glossary,
        }
    )