from django.http import HttpResponse
from django.utils.encoding import smart_str
import os
import re
import shutil
from autoslug.fields import AutoSlugField
from django.db import models
from django.db.models.signals import post_delete, pre_delete
from django.dispatch import receiver
from django.conf import settings
from django.utils.crypto import get_random_string
from django.db.models import Q

import sys
if not settings.QUAST_DIRPATH in sys.path:
    sys.path.insert(1, settings.QUAST_DIRPATH)
from quast_libs import qconfig, qutils
from quast_libs.qutils import splitext_for_fasta_file


import logging
logger = logging.getLogger('quast')


def slugify(string):
    string = string.lower()
    return re.sub(r'\W+', '-', string)


class User(models.Model):
    email = models.EmailField(blank=True, null=True)

    @staticmethod
    def create(email):
        user = User(
            email=email,
            input_dirname=email.replace('@', '_at_'))
        user.generate_password()
        user.save()
        return user

    password = models.CharField(max_length=256, blank=True, null=True)

    def generate_password(self):
        self.password = get_random_string(
            length=12,
            allowed_chars='abcdefghjkmnpqrstuvwxyz'
                          'ABCDEFGHJKLMNPQRSTUVWXYZ'
                          '123456789')
        self.save()

    input_dirname = models.CharField(max_length=256, blank=True, null=True)

    def get_dirname(self):
        return self.input_dirname

    def get_dirpath(self):
        return os.path.join(settings.RESULTS_ROOT_DIRPATH, self.get_dirname())

    default_data_set = models.ForeignKey('DataSet', related_name='+', blank=True, null=True)
    min_contig = models.IntegerField(default=qconfig.DEFAULT_MIN_CONTIG)
    scaffolds = models.BooleanField(default=False)
    eukaryotic = models.BooleanField(default=False)
    estimated_ref_size = models.IntegerField(null=True, blank=True)
    find_genes = models.BooleanField(default=False)

    def __unicode__(self):
        return self.email


class UserSession(models.Model):
    session_key = models.CharField(max_length=255, unique=True)

    @staticmethod
    def create(session_key):
        if not session_key:
            return None

        user_session = UserSession(
            session_key=session_key,
            input_dirname=session_key)

        # input_dirpath = os.path.join(settings.INPUT_ROOT_DIRPATH, user_session.input_dirname)
        # if os.path.isdir(input_dirpath):
        #     shutil.rmtree(input_dirpath)
        # os.makedirs(input_dirpath)

        user_session.save()
        return user_session

    @staticmethod
    def get_or_create(session_key):
        try:
            return UserSession.objects.get(session_key=session_key)
        except UserSession.DoesNotExist:
            return UserSession.create(session_key)

    input_dirname = models.CharField(max_length=2048)

    def get_dirname(self):
        return (self.user or self).input_dirname

    def get_dirpath(self):
        return os.path.join(settings.RESULTS_ROOT_DIRPATH, self.get_dirname())

    user = models.ForeignKey(User, null=True, blank=True)

    def get_email(self):
        return self.user.email if self.user else None

    def get_password(self):
        return self.user.password if self.user else None

    def set_user(self, user):
        user_is_fresh = not os.path.exists(user.get_dirpath())

        if user_is_fresh:  # We can copy all user_session parameters since user is fresh
            user.default_data_set = self.get_default_data_set()
            user.min_contig = self.get_min_contig()
            user.scaffolds = self.get_scaffolds()
            user.eukaryotic = self.get_eukaryotic()
            user.estimated_ref_size = self.get_estimated_ref_size()
            user.find_genes = self.get_find_genes()
            user.save()

        if self.user is None:  # Needed to move data sets and quast sessions from this user_session to user
            if user_is_fresh:  # We can just move the whole user_session folder:
                shutil.move(self.get_dirpath(), user.get_dirpath())

            else:  # User already contains a folder, so we need to merge both folders:
                for qs in self.get_quastsession_set():
                    old_dirpath = qs.get_dirpath()
                    if os.path.isdir(old_dirpath):
                        new_dirpath = qs.get_dirpath(user_dirpath=user.get_dirpath())
                        shutil.move(old_dirpath, new_dirpath)
                    qs.user = user  # TODO

                for ds in self.get_dataset_set():
                    old_dirpath = ds.get_dirpath()
                    if os.path.isdir(old_dirpath):
                        new_dirpath = ds.get_dirpath(user_dirpath=user.get_dirpath())
                        shutil.move(old_dirpath, new_dirpath)
                    ds.user = user  # TODO

        self.user = user
        self.save()

    default_data_set = models.ForeignKey('DataSet', related_name='+', blank=True, null=True)
    min_contig = models.IntegerField(default=qconfig.DEFAULT_MIN_CONTIG)
    scaffolds = models.BooleanField(default=False)
    eukaryotic = models.BooleanField(default=False)
    estimated_ref_size = models.IntegerField(null=True, blank=True)
    find_genes = models.BooleanField(default=False)

    def set_default_data_set(self, data_set):
        (self.user or self).default_data_set = data_set

    def get_default_data_set(self):
        return (self.user or self).default_data_set

    def set_min_contig(self, min_contig):
        (self.user or self).min_contig = min_contig

    def get_min_contig(self):
        return (self.user or self).min_contig

    def set_scaffolds(self, scaffolds):
        (self.user or self).scaffolds = scaffolds

    def get_scaffolds(self):
        return (self.user or self).scaffolds

    def set_eukaryotic(self, eukaryotic):
        (self.user or self).eukaryotic = eukaryotic

    def get_eukaryotic(self):
        return (self.user or self).eukaryotic

    def set_estimated_ref_size(self, estimated_ref_size):
        (self.user or self).estimated_ref_size = estimated_ref_size

    def get_estimated_ref_size(self):
        return (self.user or self).estimated_ref_size

    def set_find_genes(self, find_genes):
        (self.user or self).find_genes = find_genes

    def get_find_genes(self):
        return (self.user or self).find_genes

    # def add_quast_session(self, quast_session):
    #     if self.user:
    #         quast_session.user = self.user
    #     else:
    #         quast_session.user_session = self
    #     quast_session.save()

    def get_quastsession_set(self):
        if self.user:
            # return QuastSession.objects.filter(user_session__user=self.user)
            return QuastSession.objects.filter(user=self.user)
        else:
            return QuastSession.objects.filter(user_session=self)

    def get_all_allowed_dataset_set(self):
        if self.user:
            # return DataSet.objects.filter(Q(user_session__user=self.user) | Q(user_session__user__isnull=True))
            return DataSet.objects.filter(Q(user=self.user) | Q(user__isnull=True, user_session__isnull=True))
        else:
            return DataSet.objects.filter(Q(user_session=self) | Q(user_session__isnull=True, user__isnull=True))

    def get_dataset_set(self):
        return self.get_all_allowed_dataset_set().exclude(user_session__isnull=True, user_session__user__isnull=True,
                                                          user__isnull=True)

    def __unicode__(self):
        return self.user.__unicode__() if self.user else self.session_key

    def save(self, *args, **kwargs):
        super(UserSession, self).save(*args, **kwargs)
        if self.user:
            self.user.save()


class DataSet(models.Model):
    user_session = models.ForeignKey(UserSession, null=True, blank=True)
    user = models.ForeignKey(User, blank=True, null=True)  # TODO: Remove, not used

    name = models.CharField(max_length=1024)
    remember = models.BooleanField()

    reference_fname = models.CharField(null=True, blank=True, max_length=2048)
    genes_fname = models.CharField(null=True, blank=True, max_length=2048)
    operons_fname = models.CharField(null=True, blank=True, max_length=2048)

    dirname = AutoSlugField(populate_from='name')

    @classmethod
    def get_common_data_sets(cls):
        return DataSet.objects.filter(user__isnull=True)

    @classmethod
    def split_seq_ext(cls, fname):
        return qutils.splitext_for_fasta_file(fname)

    @classmethod
    def split_genes_ext(cls, fname):
        return os.path.splitext(fname)

    def get_dirpath(self, user_dirpath=None):
        if self.user_session:
            # Data set is created by user
            return self.__get_or_create_dirpath(
                lambda dirname: os.path.join(user_dirpath or self.user_session.get_dirpath(), 'data_sets', dirname))
        else:
            # A shared data set
            return self.__get_or_create_dirpath(
                lambda dirname: os.path.join(settings.DATA_SETS_ROOT_DIRPATH, dirname))

    def __get_or_create_dirpath(self, get_path_from_name):
        dirpath = get_path_from_name(self.dirname)

        if not os.path.isdir(dirpath):
            # What if there is a file with such name? We need to rename our dir
            base_dirname = self.dirname
            i = 1
            while os.path.exists(dirpath):
                self.dirname = base_dirname + '-' + str(i)
                dirpath = get_path_from_name(self.dirname)
                i += 1

        return dirpath

    def __unicode__(self):
        return self.name


@receiver(pre_delete, sender=DataSet)
def delete_dataset_callback(sender, **kwargs):
    dataset = sender

    # this don't work because django calls pre_delete AFTER foreign keys collected and prepared for
    # deletion, so dataset.dirname fails 
    #    dataset_dirpath = os.path.join(settings.datasets_root_dirpath, dataset.dirname)
    #    shutil.rmtree(dataset_dirpath)


class ContigsFile(models.Model):
    fname = models.CharField(max_length=2048)
    # user_session = models.ForeignKey(UserSession, null=True, blank=True)
    file_index = models.CharField(max_length=256)
    # file_size = models.IntegerField(null=True, blank=True)
    # quast_session = models.ForeignKey('QuastSession', null=True)

    def __unicode__(self):
        return self.fname

@receiver(pre_delete, sender=ContigsFile)
def delete_contigsfile_callback(sender, **kwargs):
    contigs_file = sender
    # contigs_fpath = os.path.join(settings.input_root_dirpath, contigs_file.user_session.input_dirname, contigs_file.fname)
    # if os.path.isfile(contigs_fpath):
    #     os.remove(contigs_fpath)


class QuastSession(models.Model):
    user_session = models.ForeignKey(UserSession, blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True)  # TODO: Remove, not used

    report_id = models.CharField(max_length=255, unique=True)
    link = models.CharField(max_length=2048, blank=True, null=True)
    # report_id = AutoSlugField(populate_from=(lambda instance: instance.date.strftime('%d_%b_%Y_%H_%M_%S_%f_UTC')),
    #                           unique=True,
    #                           slugify=lambda value: value)

    data_set = models.ForeignKey(DataSet, blank=True, null=True)
    contigs_files = models.ManyToManyField(ContigsFile, through='QuastSession_ContigsFile')

    min_contig = models.IntegerField(blank=True, null=True)
    scaffolds = models.BooleanField(default=False)
    eukaryotic = models.BooleanField(default=False)
    estimated_ref_size = models.IntegerField(blank=True, null=True)
    find_genes = models.BooleanField(default=False)

    caption = models.CharField(max_length=1024, blank=True, null=True)
    comment = models.TextField(max_length=200000, blank=True, null=True)
    task_id = models.CharField(max_length=1024, blank=True, null=True)
    submitted = models.BooleanField(default=True)
    date = models.DateTimeField(blank=True, null=True)
    # timezone = models.CharField(max_length=128, default='')

    @staticmethod
    def create(us):
        from django.utils import timezone
        date = timezone.now()
        report_id = date.strftime(QuastSession.get_report_id_format())

        while QuastSession.objects.filter(report_id=report_id).exists():
            date = timezone.now()
            report_id = date.strftime(QuastSession.get_report_id_format())

        qs = QuastSession(
            date=date,
            report_id=report_id,
            user_session=us,
            user=us.user,
            submitted=False,
            data_set=us.get_default_data_set(),
            min_contig=us.get_min_contig(),
            scaffolds=us.get_scaffolds(),
            eukaryotic=us.get_eukaryotic(),
            estimated_ref_size=us.get_estimated_ref_size(),
            find_genes=us.get_find_genes())

        result_dirpath = qs.get_dirpath()
        if os.path.exists(result_dirpath):
            logger.critical('results_dirpath "%s" already exists' % result_dirpath)
            raise Exception('results_dirpath "%s" already exists' % result_dirpath)

        os.makedirs(result_dirpath)
        logger.info('created result dirpath: %s' % result_dirpath)

        contigs_dirpath = qs.get_contigs_dirpath()
        os.makedirs(contigs_dirpath)
        logger.info('created contigs dirpath: %s' % contigs_dirpath)

        qs.save()
        return qs

    @staticmethod
    def get_report_id_format():
        return '%d_%b_%Y_%H_%M_%S_%f'

    def generate_link(self):  # needs caption
        if self.caption is None:
            logger.warn('QuastSession.get_report_link before setting up caption')
        time = self.date.strftime('%d_%b_%Y_%H:%M:%S_%f')
        self.link = time + slugify(('_' + self.caption) if self.caption else '')

    def get_report_html_link(self):
        return os.path.join(settings.REPORT_LINK_BASE, self.link or self.report_id) + '/report.html'

    def get_report_download_link(self):
        return os.path.join(settings.REPORT_LINK_BASE, 'download', self.link or self.report_id)

    def get_icarus_html_link(self):
        return os.path.join(settings.REPORT_LINK_BASE, self.link or self.report_id) + '/icarus.html'

    def get_icarus_alignment_viewer_html_link(self):
        return os.path.join(settings.REPORT_LINK_BASE, self.link or self.report_id) + '/icarus/contig_alignment_viewer.html'

    def get_icarus_contig_size_viewer_html_link(self):
        return os.path.join(settings.REPORT_LINK_BASE, self.link or self.report_id) + '/icarus/contig_size_viewer.html'

    def get_download_name(self):
        return 'quast_report_' + self.report_id + slugify('_' + self.caption if self.caption else '')

    def get_dirname(self):
        return str(self.report_id)

    def get_dirpath(self, user_dirpath=None):
        return os.path.join(user_dirpath or self.user_session.get_dirpath(), self.get_dirname())

    def get_contigs_dirpath(self):
        return os.path.join(self.get_dirpath(), 'contigs')

    def __unicode__(self):
        string = ''
        if self.caption:
            string = self.caption + ' '
        string += self.date.strftime('%d %b %Y %H:%M:%S.%f %z')
        return string


class QuastSession_ContigsFile(models.Model):
    quast_session = models.ForeignKey(QuastSession)
    contigs_file = models.ForeignKey(ContigsFile)


