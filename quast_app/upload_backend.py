from io import BufferedWriter, FileIO
import os
from ajaxuploader.backends.base import AbstractUploadBackend


class MyBaseUploadBackend(AbstractUploadBackend):
    def __init__(self, upload_dir, **kwargs):
        super(MyBaseUploadBackend, self).__init__(**kwargs)
        self.upload_dir = os.path.join('__tmp', upload_dir)

    def setup(self, filename):
        self._path = os.path.join(self.upload_dir, filename)
        try:
            os.makedirs(os.path.realpath(os.path.dirname(self._path)))
        except:
            pass
        self._dest = BufferedWriter(FileIO(self._path, "w"))

    def upload_chunk(self, chunk):
        self._dest.write(chunk)

    def upload_complete(self, request, filename):
        path = os.path.join(self.upload_dir, filename)
        self._dest.close()
        return {'path': path }



class ContigsUploadBackend(MyBaseUploadBackend):
    def __init__(self, **kwargs):
        super(ContigsUploadBackend, self).__init__('contigs', **kwargs)

    def update_filename(self, request, filename):
        return os.path.join(request.session['upload_directory'], 'contigs', filename)


class ReferenceUploadBackend(MyBaseUploadBackend):
    def __init__(self, **kwargs):
        super(ReferenceUploadBackend, self).__init__('reference', **kwargs)

    def update_filename(self, request, filename):
        return os.path.join(request.session['upload_directory'], 'reference', filename)


class GenesUploadBackend(MyBaseUploadBackend):
    def __init__(self, **kwargs):
        super(GenesUploadBackend, self).__init__('genes', **kwargs)

    def update_filename(self, request, filename):
        return os.path.join(request.session['upload_directory'], 'genes', filename)


class OperonsUploadBackend(MyBaseUploadBackend):
    def __init__(self, **kwargs):
        super(OperonsUploadBackend, self).__init__('operons', **kwargs)

    def update_filename(self, request, filename):
        return os.path.join(request.session['upload_directory'], 'operons', filename)
