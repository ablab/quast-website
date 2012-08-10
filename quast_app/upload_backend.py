from io import BufferedWriter, FileIO
import os
from ajaxuploader.backends.base import AbstractUploadBackend
from quast_app.models import ContigsFileName, UserSession
from quast_website import settings


class MyBaseUploadBackend(AbstractUploadBackend):
    def __init__(self, dirname, **kwargs):
        super(MyBaseUploadBackend, self).__init__(**kwargs)
        self.dirname = dirname
        self.upload_root = settings.input_root_dirpath

    def setup(self, filename):
        dirpath = os.path.join(self.upload_root, self.session_key, self.dirname)
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
        dirpath = os.path.join(self.upload_root, self.session_key, self.dirname)
        fpath = os.path.join(dirpath, filename)
        self._dest.close()

        user_session = UserSession.objects.get(session_key=self.session_key)
        c_fn = ContigsFileName(fname=filename, user_session=user_session)
        c_fn.save()
        return {'path': fpath }

    def update_filename(self, request, filename):
        self.session_key = request.session.session_key
        return filename


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
