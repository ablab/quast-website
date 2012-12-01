from datetime import datetime
import shutil
from autoslug.fields import AutoSlugField
from django.db import models
from django.db.models.signals import post_delete, pre_delete
from django.dispatch import receiver
import os
import sys
import re
from django.conf import settings

import logging
logger = logging.getLogger('quast')


def slugify(str):
    str = str.lower()
    return re.sub(r'\W+','-',str)


class UserSession(models.Model):
    session_key = models.CharField(max_length=256)
    input_dirname = models.CharField(max_length=2048)
    email = models.EmailField(blank=True, null=True)

    def __unicode__(self):
        return self.session_key


class Dataset(models.Model):
    name = models.CharField(max_length=1024)
    remember = models.BooleanField()

    reference_fname = models.CharField(null=True, blank=True, max_length=2048)
    genes_fname = models.CharField(null=True, blank=True, max_length=2048)
    operons_fname = models.CharField(null=True, blank=True, max_length=2048)

    dirname = AutoSlugField(populate_from='name', unique=True)

    def get_dirpath(self):
        return os.path.join(settings.DATA_SETS_ROOT_DIRPATH, self.dirname)

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
    user_session = models.ForeignKey('UserSession', null=True, blank=True, default=None)
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

#
#class QuastSession2(models.Model):
#    def __init__(self, user_session, *args, **kwargs):
#        from datetime import datetime
#        now_datetime = datetime.now()
#
#        super(QuastSession2, self).__init__(date=now_datetime,
#                                           user_session=user_session,
#                                           submited=False,
#                                           *args, **kwargs)
#
#    user_session = models.ForeignKey(UserSession)
#    dataset = models.ForeignKey(Dataset, blank=True, null=True)
#    task_id = models.CharField(max_length=1024, blank=True, null=True)
#    contigs_files = models.ManyToManyField(ContigsFile)
#    caption = models.CharField(max_length=1024, blank=True, null=True)
#    comment = models.TextField(max_length=200000, blank=True, null=True)
#    min_contig = models.IntegerField(blank=True, null=True)
#
#    submited = models.BooleanField(default=True)
#    date = models.DateTimeField()
#    report_id = AutoSlugField(populate_from=(lambda instance: instance.date.strftime('%d_%b_%Y_%H:%M:%S.%f')),
#                              unique=True,
#                              slugify=lambda value: value.replace(' ', '_'))
#
#    def get_report_link(self):  # needs caption
#        if not self.caption:
#            logging.warn('QuastSession.get_report_link before setting up caption')
#
#        return self.report_id + ('_' + self.caption if self.caption else '')
#
#    def get_reldirpath(self):
#        return self.user_session.session_key + '/' + str(self.report_id)
#
#    def get_dirpath(self):
#        return os.path.join(settings.RESULTS_ROOT_DIRPATH, self.get_reldirpath())
#
#    def get_contigs_dirpath(self):
#        return os.path.join(self.get_dirpath(), 'contigs')
#
#    def __unicode__(self):
#        str = ''
#        if self.caption:
#            str = self.caption + ' '
#        str += self.date.strftime('%d %b %Y %H:%M:%S.%f')
#        return str



class QuastSession(models.Model):
#    def __init__(self, user_session, *args, **kwargs):
#        from datetime import datetime
#        now_datetime = datetime.now()
#
#        super(QuastSession, self).__init__(date=now_datetime,
#                                           user_session=user_session,
#                                           submited=False,
#                                           *args, **kwargs)

    user_session = models.ForeignKey(UserSession)
    dataset = models.ForeignKey(Dataset, blank=True, null=True)
    task_id = models.CharField(max_length=1024, blank=True, null=True)
    contigs_files = models.ManyToManyField(ContigsFile, through='QuastSession_ContigsFile')
    caption = models.CharField(max_length=1024, blank=True, null=True)
    comment = models.TextField(max_length=200000, blank=True, null=True)
#    min_contig = models.IntegerField(blank=True, null=True)

    submited = models.BooleanField(default=True)
    date = models.DateTimeField()
#    timezone = models.CharField(max_length=128, default='')
    report_id = models.CharField(max_length=256, unique=True)
    link = models.CharField(max_length=2048, blank=True, null=True)
#    report_id = AutoSlugField(populate_from=(lambda instance: instance.date.strftime('%d_%b_%Y_%H_%M_%S_%f_UTC')),
#                              unique=True,
#                              slugify=lambda value: value)

#    def set_report_id_compatible_with_link(self):
#        return time + slugify('_' +  self.caption if self.caption else '')

    @classmethod
    def get_report_id_format(cls):
        return '%d_%b_%Y_%H_%M_%S_%f_UTC'

    def generate_link(self):  # needs caption
        if not self.caption:
            logging.warn('QuastSession.get_report_link before setting up caption')
        time = self.date.strftime('%d_%b_%Y_%H:%M:%S_%f_UTC')
        self.link = time + slugify('_' +  self.caption if self.caption else '')

    def get_download_name(self):
        return 'quast_report_' + self.report_id + slugify('_' +  self.caption if self.caption else '')

    def get_reldirpath(self):
        return self.user_session.session_key + '/' + str(self.report_id)

    def get_dirpath(self):
        return os.path.join(settings.RESULTS_ROOT_DIRPATH, self.get_reldirpath())

    def get_contigs_dirpath(self):
        return os.path.join(self.get_dirpath(), 'contigs')

    def get_evaluation_contigs_dirpath(self):
        return self.get_contigs_dirpath() + '_evaluation'

    def __unicode__(self):
        str = ''
        if self.caption:
            str = self.caption + ' '
        str += self.date.strftime('%d %b %Y %H:%M:%S.%f %z')
        return str


class QuastSession_ContigsFile(models.Model):
    quast_session = models.ForeignKey(QuastSession)
    contigs_file = models.ForeignKey(ContigsFile)


