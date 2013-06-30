import os
from django.conf import settings
from django.http import HttpResponse, Http404
from django.core.servers.basehttp import FileWrapper
from views_report import get_report_response_dict
from django.shortcuts import render_to_response
from django.utils.encoding import smart_str
import mimetypes


download_text = '' +\
    'Text, TSV and Latex versions<br>' +\
    'of the table, plots in PNG.<br>' +\
    '<div class="small_line_indent"></div>'


def e_coli(request, download_fname):
    return common_view('paper/', 'E. coli', 'e.coli', download_fname)


def h_sapiens(request, download_fname):
    return common_view('paper/', 'H. sapiens chr. 14', 'h.sapiens_chr14', download_fname)


def b_impatiens(request, download_fname):
    return common_view('paper/', 'B. impatiens', 'b.impatiens', download_fname)


def e_coli_sc(request, download_fname):
    return common_view('', 'E. coli, single cell', 'e.coli-single-cell', download_fname)


def e_coli_mc(request, download_fname):
    return common_view('', 'E. coli, isolate', 'e.coli-isolate', download_fname)


def common_view(dir_name, caption, slug_name, download_fname):
    if download_fname:
        download_fpath = os.path.join(settings.FILES_DOWNLOADS_DIRPATH, slug_name, download_fname)

        if os.path.exists(download_fpath):
#            if download_fname[-4:] == '.zip':
#                mimetype = 'application/zip'
#            else:
#            mimetype = 'application/force-download'

#            f = FileWrapper(fpath)
#            response = HttpResponse(mimetype=mimetype)
#            response['Content-Disposition'] = 'attachment; filename=%s' % download_fname
#            response['X-Sendfile'] = download_fpath
#            response['Content-Length'] = 100
#            return response

            wrapper = FileWrapper(open(download_fpath, 'r'))
            content_type = mimetypes.guess_type(download_fpath)[0]

            response = HttpResponse(wrapper, content_type=content_type)
            response['Content-Length'] = os.path.getsize(download_fpath)
            response['Content-Disposition'] = 'attachment; filename=' + smart_str(download_fname)

            return response

        else:
            raise Http404('File %s does not exist' % download_fname)

    else:
        response_dict = settings.TEMPLATE_ARGS_BY_DEFAULT

        report_dict = get_report_response_dict(
            os.path.join(settings.PAPER_DIRPATH, slug_name),
            caption=caption,
        )
        response_dict.update(report_dict)

        response_dict['download'] = True
        response_dict['downloadLink'] = slug_name + '_quast_report.zip'
        response_dict['downloadText'] = download_text

        return render_to_response(dir_name + slug_name + '.html', response_dict)


def paper(request):
    return render_to_response('paper/index.html')