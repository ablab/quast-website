import os
import re
import shutil
from autoslug.fields import AutoSlugField
from django.db import models
from django.db.models.signals import post_delete, pre_delete
from django.dispatch import receiver
from django.conf import settings
from django.utils.crypto import get_random_string


import logging
logger = logging.getLogger('quast')


def slugify(str):
    str = str.lower()
    return re.sub(r'\W+', '-', str)


class User(models.Model):
    input_dirname = models.CharField(max_length=256, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    password = models.CharField(max_length=256, blank=True, null=True)

    def get_dirname(self):
        return self.input_dirname

    @staticmethod
    def create(email):
        user = User(
            email=email,
            input_dirname=email.replace('@', '_')
        )
        user.save()
        user.generate_password()
        return user

    def generate_password(self):
        self.password = get_random_string(
            length=12,
            allowed_chars='abcdefghjkmnpqrstuvwxyz'
                          'ABCDEFGHJKLMNPQRSTUVWXYZ'
                          '123456789'
        )
        self.save()


class UserSession(models.Model):
    session_key = models.CharField(max_length=256, unique=True)
    input_dirname = models.CharField(max_length=2048)
    user = models.ForeignKey('User', null=True, blank=True)

    def get_email(self):
        return self.user.email if self.user else None

    def get_password(self):
        return self.user.password if self.user else None

    def get_dirname(self):
        return (self.user or self).input_dirname

    # def add_quast_session(self, quast_session):
    #     if self.user:
    #         quast_session.user = self.user
    #     else:
    #         quast_session.user_session = self
    #     quast_session.save()

    def get_quastsession_set(self):
        return (self.user or self).quastsession_set

    def set_user(self, user):
        # session_input_dirpath = os.path.join(settings.INPUT_ROOT_DIRPATH, self.input_dirname)
        # user_input_dirpath = os.path.join(settings.INPUT_ROOT_DIRPATH, user.input_dirname)
        # os.rename(session_input_dirpath, user_input_dirpath)

        if self.user is None:
            session_results_dirpath = os.path.join(settings.RESULTS_ROOT_DIRPATH, self.input_dirname)
            if not session_results_dirpath:
                user_results_dirpath = os.path.join(settings.RESULTS_ROOT_DIRPATH, user.input_dirname)
                os.rename(session_results_dirpath, user_results_dirpath)

                if not os.path.isdir(user_results_dirpath):
                    logger.error('Directory %s does no exist', user_results_dirpath)
                    return

            for qs in self.quastsession_set.all():
                qs.user = user
                qs.user_session = None
                qs.save()

        self.user = user
        self.save()


    def __unicode__(self):
        return self.session_key

    @staticmethod
    def create(session_key):
        if not session_key:
            return None

        user_session = UserSession(
            session_key=session_key,
            input_dirname=session_key
        )

        # input_dirpath = os.path.join(settings.INPUT_ROOT_DIRPATH, user_session.input_dirname)
        # if os.path.isdir(input_dirpath):
        #     shutil.rmtree(input_dirpath)
        # os.makedirs(input_dirpath)

        return user_session

    @staticmethod
    def get_or_create(session_key):
        try:
            return UserSession.objects.get(session_key=session_key)
        except UserSession.DoesNotExist:
            return UserSession.create(session_key)


class DataSet(models.Model):
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

@receiver(pre_delete, sender=DataSet)
def delete_dataset_callback(sender, **kwargs):
    dataset = sender

    # this don't work because django calls pre_delete AFTER foreign keys collected and prepared for
    # deletion, so dataset.dirname fails 
    #    dataset_dirpath = os.path.join(settings.datasets_root_dirpath, dataset.dirname)
    #    shutil.rmtree(dataset_dirpath)


class ContigsFile(models.Model):
    fname = models.CharField(max_length=2048)
    user_session = models.ForeignKey('UserSession', null=True, blank=True)
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
    user = models.ForeignKey(User, blank=True, null=True)

    report_id = models.CharField(max_length=256, unique=True)
    link = models.CharField(max_length=2048, blank=True, null=True)
    # report_id = AutoSlugField(populate_from=(lambda instance: instance.date.strftime('%d_%b_%Y_%H_%M_%S_%f_UTC')),
    #                           unique=True,
    #                           slugify=lambda value: value)

    data_set = models.ForeignKey(DataSet, blank=True, null=True)
    contigs_files = models.ManyToManyField(ContigsFile, through='QuastSession_ContigsFile')

    caption = models.CharField(max_length=1024, blank=True, null=True)
    comment = models.TextField(max_length=200000, blank=True, null=True)
    min_contig = models.IntegerField(blank=True, null=True)
    task_id = models.CharField(max_length=1024, blank=True, null=True)
    submitted = models.BooleanField(default=True)
    date = models.DateTimeField()
    # timezone = models.CharField(max_length=128, default='')

    @classmethod
    def create(cls, user_session):
        from django.utils import timezone
        date = timezone.now()
        report_id = date.strftime(QuastSession.get_report_id_format())

        while QuastSession.objects.filter(report_id=report_id).exists():
            date = timezone.now()
            report_id = date.strftime(QuastSession.get_report_id_format())

        quast_session = QuastSession(date=date,
                                     report_id=report_id,
                                     submitted=False)
        if user_session.user:
            quast_session.user = user_session.user
        else:
            quast_session.user_session = user_session

        quast_session.save()

        result_dirpath = quast_session.get_dirpath()
        if os.path.isdir(result_dirpath):
            logger.critical('results_dirpath "%s" already exists' % result_dirpath)
            raise Exception('results_dirpath "%s" already exists' % result_dirpath)

        os.makedirs(result_dirpath)
        logger.info('created result dirpath: %s' % result_dirpath)

        os.makedirs(quast_session.get_contigs_dirpath())
        logger.info('created contigs dirpath: %s' % result_dirpath)

        return quast_session

    @classmethod
    def get_report_id_format(cls):
        return '%d_%b_%Y_%H_%M_%S_%f_UTC'

    def generate_link(self):  # needs caption
        if self.caption is None:
            logger.warn('QuastSession.get_report_link before setting up caption')
        time = self.date.strftime('%d_%b_%Y_%H:%M:%S_%f_UTC')
        self.link = time + slugify('_' +  self.caption if self.caption else '')

    def get_download_name(self):
        return 'quast_report_' + self.report_id + \
               slugify('_' +  self.caption if self.caption else '')

    def get_reldirpath(self):
        return (self.user_session or self.user).get_dirname() + '/' + str(self.report_id)

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


