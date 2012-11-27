from io import BufferedWriter, FileIO
from django.db import DatabaseError
from django.http import HttpResponseBadRequest
import os
import random
from ajaxuploader.backends.base import AbstractUploadBackend
from models import ContigsFile, UserSession
from django.conf import settings

import logging
logger = logging.getLogger('quast')


class MyBaseUploadBackend(AbstractUploadBackend):
    def __init__(self, dirname, **kwargs):
        super(MyBaseUploadBackend, self).__init__(**kwargs)
        self.user_session = None


    def setup(self, filename):
        dirpath = os.path.join(settings.INPUT_ROOT_DIRPATH, self.user_session.input_dirname)
        try:
            os.makedirs(dirpath)
        except:
            pass

        fpath = os.path.join(dirpath, filename)
        self._path = fpath
        self._dest = BufferedWriter(FileIO(self._path, 'w'))


    def upload_chunk(self, chunk):
        self._dest.write(chunk)


    def upload_complete(self, request, filename):
        self._dest.close()

        file_index = "%x" % random.getrandbits(128)
        c_fn = ContigsFile(fname=filename, user_session=self.user_session, file_index=file_index)
        c_fn.save()
        return {
            'file_index': file_index,
        }


    def update_filename(self, request, filename):
        dirpath = os.path.join(settings.INPUT_ROOT_DIRPATH, self.user_session.input_dirname)
        fpath = os.path.join(dirpath, filename)

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
            logger.error('uploader_backend.remove: Request.GET must contain "fileNames"')
            return False, 'Request.GET must contain "fileNames"'


        file_index = request.GET['fileIndex']
        try:
            contigs_file = ContigsFile.objects.get(file_index=file_index)
        except ContigsFile.DoesNotExist:
            logger.error('uploader_backend.remove: No file with such index %d' % file_index)
            return False, 'No file with such index'

        fname = contigs_file.fname

        if contigs_file.user_session != self.user_session:
            logger.error('uploader_backend.remove: This file (%s) belongs to session %s, this session is %s'
                         % (fname, str(contigs_file.user_session ), str(self.user_session.session_key)))
            return False, 'This file does not belong to this session'


        contigs_fpath = os.path.join(settings.INPUT_ROOT_DIRPATH,
                                     self.user_session.input_dirname,
                                     contigs_file.fname)
        if os.path.isfile(contigs_fpath):
            try:
                os.remove(contigs_fpath)
            except IOError as e:
                logger.error('uploader_backend.remove: IOError when removing "%s", fileIndex=%d": %s' % (fname, file_index, e.message))
                return False, 'Cannot remove file'

        try:
            contigs_file.delete()
        except DatabaseError as e:
            logger.warn('uploader_backend.remove: DatabaseError when removing "%s", fileIndex=%d: %s' % (fname, file_index, e.message))
            return False, 'Data base error when removing file'
        except Exception as e:
            logger.error('uploader_backend.remove: Exception when removing "%s", fileIndex=%d: %s' % (fname, file_index, e.message))
            return False, 'Data base exception when removing file'

        logger.info('uploader_backend.remove_all: Successfully removed "%s", fileIndex=%d' % (fname, file_index))
        return True, ''


    def remove_all(self, request):
        if 'fileNames' not in request.GET:
            logger.error('remove_all: Request.GET must contain "fileNames"')
            return False

        file_names_one_string = request.GET['fileNames']
        file_names = file_names_one_string.split('\n')[:-1]

        this_user_contigs_files = ContigsFile.objects.filter(user_session=self.user_session)

        for fname in file_names:
            found = this_user_contigs_files.filter(fname=fname)

            if len(found) == 0:
                logger.error('uploader_backend.remove_all: No file "%s" when trying to remove all' % fname)
            else:
                contigs_file = found[0]
                if contigs_file.user_session != self.user_session:
                    logger.error('uploader_backend.remove_all: File "%s" does not belong to this session "%s"' \
                          % (fname, self.user_session.session_key))
                else:
                    contigs_fpath = os.path.join(settings.INPUT_ROOT_DIRPATH,
                                                 self.user_session.input_dirname,
                                                 contigs_file.fname)
                    if os.path.isfile(contigs_fpath):
                        try:
                            os.remove(contigs_fpath)
                        except IOError as e:
                            logger.error('uploader_backend.remove_all: IOError when removing "%s": %s' % (fname, e.message))
                    try:
                        contigs_file.delete()
                        logger.info('uploader_backend.remove_all: Successfully removed "%s"' % fname)
                    except DatabaseError as e:
                        logger.error('uploader_backend.remove_all: DatabaseError when removing "%s": %s' % (fname, e.message))
                    except Exception as e:
                        logger.error('uploader_backend.remove_all: Exception when removing "%s": %s' % (fname, e.message))

        return True


    def get_uploads(self, request):
        contigs_files = ContigsFile.objects.filter(user_session=self.user_session)
        return [{"fileName": c_f.fname,
                 "fileIndex": c_f.file_index,
                 "file_index": c_f.file_index,
#                 "fileSize": c_f.file_size if c_f.file_size else None,
                 }
                for c_f in contigs_files]



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


