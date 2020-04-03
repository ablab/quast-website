from django.shortcuts import render_to_response
import os
from models import DataSet


def add_refs(request):
    DataSet.objects.filter(user__isnull=True).delete()
    dataset = DataSet(
        name = 'E. coli, first 10 kb',
        remember = True,
        genes_fname = 'genes.txt',
        operons_fname = 'operons.txt',
        reference_fname = 'e_coli_10k.fasta',
        dirname = 'e_coli_10k',
        user_session = None,
        user = None
    )
    dataset.save()

    dataset = DataSet(
        name = 'E. coli',
        remember = True,
        genes_fname = 'genes.txt',
        operons_fname = 'operons.txt',
        reference_fname = 'reference.fa',
        dirname = 'e_coli',
        user_session = None,
        user = None
    )
    dataset.save()

    dataset = DataSet(
        name = 'SARS-CoV-2',
        remember = True,
        reference_fname = 'sars_cov2.fasta',
        dirname = 'sars_cov2',
        user_session = None,
        user = None
    )
    dataset.save()
