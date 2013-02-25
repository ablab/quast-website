from io import BufferedWriter, FileIO
from django.db import DatabaseError
from django.http import HttpResponseBadRequest
import os
import random
from ajaxuploader.backends.base import AbstractUploadBackend
from models import ContigsFile, UserSession, QuastSession, QuastSession_ContigsFile
from django.conf import settings

import logging
logger = logging.getLogger('quast')


class MyBaseUploadBackend(AbstractUploadBackend):
    def __init__(self, dirname, **kwargs):
        super(MyBaseUploadBackend, self).__init__(**kwargs)
        self.report_id = None

    def set_report_id(self, report_id):
        self.report_id = report_id
        try:
            self.quast_session = QuastSession.objects.get(report_id=self.report_id)
            return True
        except QuastSession.DoesNotExist:
            logger.error('No quast session with report_id=%s' % self.report_id)
            return False

    def setup(self, filename):
        dirpath = self.quast_session.get_contigs_dirpath()
        logger.info('filename is %s' % filename)
        logger.info('contigs dirpath is %s' % dirpath)

        if not os.path.exists(dirpath):
            logger.error("contigs directory doesn't exist")
            return False

        fpath = os.path.join(dirpath, filename)

        self._path = fpath
        self._dest = BufferedWriter(FileIO(self._path, 'w'))
        return True

    def upload_chunk(self, chunk):
        self._dest.write(chunk)

    def upload_complete(self, request, filename):
        self._dest.close()

        file_index = "%x" % random.getrandbits(128)
        c_fn = ContigsFile(fname=filename, file_index=file_index)
        c_fn.save()
        qc = QuastSession_ContigsFile(contigs_file=c_fn, quast_session=self.quast_session)
        qc.save()

        logger.info('%s' % filename)

        return {
            'file_index': file_index,
        }

    def update_filename(self, request, filename):
        dirpath = self.quast_session.get_contigs_dirpath()
        logger.info('contigs dirpath is %s' % dirpath)

        fpath = os.path.join(dirpath, filename)
        logger.info('file path is %s' % fpath)

        i = 2
        base_fpath = fpath
        base_filename = filename
        while os.path.isfile(fpath):
            fpath = str(base_fpath) + '__' + str(i)
            filename = str(base_filename) + '__' + str(i)
            i += 1

        return filename

    def remove(self, request):
        if 'fileIndex' not in request.GET:
            logger.error('Request.GET must contain "fileIndex"')
            return False, 'Request.GET must contain "fileIndex"'

        file_index = request.GET['fileIndex']
        try:
            contigs_file = self.quast_session.contigs_files.get(file_index=file_index)
        except ContigsFile.DoesNotExist:
            logger.error('No file with such index %d in this quast_session' % file_index)
            return False, 'No file with such index'

        success, msg = self.__remove(contigs_file)
        return success, msg

#        if contigs_file.user_session != self.user_session:
#            logger.error('This file (%s) belongs to session %s, this session is %s'
#                         % (fname, str(contigs_file.user_session ), str(self.user_session.session_key)))
#            return False, 'This file does not belong to this session'


    def __remove(self, contigs_file):
        fname = contigs_file.fname
        contigs_fpath = os.path.join(self.quast_session.get_contigs_dirpath(), fname)

        if os.path.isfile(contigs_fpath):
            try:
                os.remove(contigs_fpath)
            except IOError as e:
                logger.error('IOError when removing "%s", fileIndex=%d": %s' % (fname, file_index, e.message))
                return False, 'Cannot remove file'

        try:
            contigs_file.delete()
        except DatabaseError as e:
            logger.warn('DatabaseError when removing "%s", fileIndex=%d: %s' % (fname, file_index, e.message))
            return False, 'Data base error when removing file'
        except Exception as e:
            logger.error('Exception when removing "%s", fileIndex=%d: %s' % (fname, file_index, e.message))
            return False, 'Data base exception when removing file'

        return True, ''

    def remove_all(self, request):
#        if 'fileNames' not in request.GET:
#            logger.error('remove_all: Request.GET must contain "fileNames"')
#            return False
#
#        file_names_one_string = request.GET['fileNames']
#        file_names = file_names_one_string.split('\n')[:-1]

#        this_user_contigs_files = ContigsFile.objects.filter(user_session=self.user_session)

        logger.info('uploader_backend.remove_all')
        for c_f in self.quast_session.contigs_files.all():
            success, msg = self.__remove(c_f)

        return True

    def get_uploads(self, request):
        contigs_files = self.quast_session.contigs_files.all()

        return [{"fileName": c_f.fname,
                 "fileIndex": c_f.file_index,
                 "file_index": c_f.file_index,
               # "fileSize": c_f.file_size if c_f.file_size else None,
                 } for c_f in contigs_files]


class ContigsUploadBackend(MyBaseUploadBackend):
    def __init__(self, **kwargs):
        super(ContigsUploadBackend, self).__init__('contigs', **kwargs)


class ReferenceUploadBackend(MyBaseUploadBackend):
    def __init__(self, **kwargs):
        super(ReferenceUploadBackend, self).__init__('reference', **kwargs)


class GenesUploadBackend(MyBaseUploadBackend):
    def __init__(self, **kwargs):
        super(GenesUploadBackend, self).__init__('genes', **kwargs)


class OperonsUploadBackend(MyBaseUploadBackend):
    def __init__(self, **kwargs):
        super(OperonsUploadBackend, self).__init__('operons', **kwargs)


