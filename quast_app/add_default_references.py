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
        name = 'E. coli strain K-12 substrain MG1655',
        remember = True,
        genes_fname = 'genes.txt',
        reference_fname = 'reference.fa',
        dirname = 'e_coli',
        user_session = None,
        user = None
    )
    dataset.save()

    dataset = DataSet(
        name = 'E. coli strain K-12 substrain W3110',
        remember = True,
        genes_fname = 'genes.gff',
        reference_fname = 'reference.fa',
        dirname = 'e_coli_w3110',
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

    dataset = DataSet(
        name = 'S. aureus NCTC 8325',
        remember = True,
        genes_fname = 'genes.gff',
        reference_fname = 'reference.fasta',
        dirname = 's_aureus',
        user_session = None,
        user = None
    )
    dataset.save()

    dataset = DataSet(
        name = 'K. pneumoniae HS11286',
        remember = True,
        genes_fname = 'genes.gff',
        reference_fname = 'reference.fasta',
        dirname = 'k_pneumoniae',
        user_session = None,
        user = None
    )
    dataset.save()

    dataset = DataSet(
        name = 'S. cerevisiae S288C',
        remember = True,
        genes_fname = 'genes.gff',
        reference_fname = 'reference.fasta',
        dirname = 's_cerevisiae',
        user_session = None,
        user = None
    )
    dataset.save()

    dataset = DataSet(
        name = 'C. elegans WBcel235',
        remember = True,
        genes_fname = 'genes.gff',
        reference_fname = 'reference.fasta',
        dirname = 'c_elegans',
        user_session = None,
        user = None
    )
    dataset.save()

    dataset = DataSet(
        name = 'D. melanogaster Release 6 plus ISO1 MT',
        remember = True,
        genes_fname = 'genes.gff',
        reference_fname = 'reference.fasta',
        dirname = 'd_melanogaster',
        user_session = None,
        user = None
    )
    dataset.save()