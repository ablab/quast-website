import logging
logger = logging.getLogger('quast')
mailer = logging.getLogger('quast_mailer')

class AbstractUploadBackend(object):
    BUFFER_SIZE = 1 * 1024 * 1024  # 10MB

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def setup(self, filename):
        """Responsible for doing any pre-processing needed before the upload
        starts."""

    def update_filename(self, request, filename):
        """Returns a new name for the file being uploaded."""

    def upload_chunk(self, chunk):
        """Called when a string was read from the client, responsible for 
        writing that string to the destination file."""
        raise NotImplementedError

    def upload_complete(self, request, filename):
        """Overriden to performs any actions needed post-upload, and returns
        a dict to be added to the render / json context"""

    def upload(self, uploaded, filename, raw_data, max_size=None):
        if raw_data:
            mailer.info('uploaded raw data via ajax and is being streamed')

            # File was uploaded via ajax, and is streaming in.
            total_size = 0
            chunk = uploaded.read(self.BUFFER_SIZE)
            while len(chunk) > 0:
                total_size += self.BUFFER_SIZE
                if max_size is not None and total_size > max_size * 1024 * 1024:
                    return False
                self.upload_chunk(chunk)
                chunk = uploaded.read(self.BUFFER_SIZE)
        else:
            mailer.info('uploaded via a POST and is here')

            # File was uploaded via a POST, and is here.
            total_size = 0
            for chunk in uploaded.chunks():
                total_size += self.BUFFER_SIZE
                if max_size and total_size > max_size:
                    return False
                self.upload_chunk(chunk)
        return True
