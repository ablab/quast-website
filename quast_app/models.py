import shutil
from autoslug.fields import AutoSlugField
from django.db import models
from django.db.models.signals import post_delete, pre_delete
from django.dispatch import receiver
import os
import sys
from django.conf import settings


class UserSession(models.Model):
    session_key = models.CharField(max_length=256)
    input_dirname = models.CharField(max_length=2048)

    def __unicode__(self):
        return self.session_key


class Dataset(models.Model):
    name = models.CharField(max_length=1024)
    remember = models.BooleanField()

    reference_fname = models.CharField(null=True, blank=True, max_length=2048)
    genes_fname = models.CharField(null=True, blank=True, max_length=2048)
    operons_fname = models.CharField(null=True, blank=True, max_length=2048)

    dirname = AutoSlugField(populate_from='name', unique=True)

    def __unicode__(self):
        return self.name

@receiver(pre_delete, sender=Dataset)
def delete_dataset_callback(sender, **kwargs):
    dataset = sender

    # this don't work because django calls pre_delete AFTER foreign keys collected and prepared for
    # deletion, so dataset.dirname fails 
#    dataset_dirpath = os.path.join(settings.datasets_root_dirpath, dataset.dirname)
#    shutil.rmtree(dataset_dirpath)



class ContigsFile(models.Model):
    fname = models.CharField(max_length=2048)
    user_session = models.ForeignKey('UserSession')
    file_index = models.CharField(max_length=256)
#    file_size = models.IntegerField(null=True, blank=True)
#   quast_session = models.ForeignKey('QuastSession', null=True)

    def __unicode__(self):
        return self.fname

@receiver(pre_delete, sender=ContigsFile)
def delete_contigsfile_callback(sender, **kwargs):
    contigs_file = sender

#    contigs_fpath = os.path.join(settings.input_root_dirpath, contigs_file.user_session.input_dirname, contigs_file.fname)
#    if os.path.isfile(contigs_fpath):
#        os.remove(contigs_fpath)


class QuastSession(models.Model):
    user_session = models.ForeignKey(UserSession)
    dataset = models.ForeignKey(Dataset, null=True)
    task_id = models.CharField(max_length=1024, null=True)
    contigs_files = models.ManyToManyField(ContigsFile, through='QuastSession_ContigsFile')

    date = models.DateTimeField()

    report_id = AutoSlugField(populate_from=(lambda instance: instance.date.strftime('%d_%b_%Y_%H:%M:%S.%f')),
                              unique=True,
                              slugify=(lambda s: s))

    def get_results_reldirpath(self):
        return self.user_session.session_key + '/' + self.report_id.__str__()

    def __unicode__(self):
        return self.date.strftime('%d %b %Y %H:%M:%S.%f')


class QuastSession_ContigsFile(models.Model):
    quast_session = models.ForeignKey(QuastSession)
    contigs_file = models.ForeignKey(ContigsFile)


