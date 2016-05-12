import os
from django.conf import settings
from django.http import HttpResponse, Http404
from wsgiref.util import FileWrapper
# from django.core.files.base import ContentFile
import mimetypes
from views_report import get_report_response_dict, get_icarus_menu_response_dict, get_icarus_response_dict
from django.shortcuts import render_to_response
from django.utils.encoding import smart_str


download_text = '' +\
    'Text, TSV and Latex versions<br>' +\
    'of the table, plots in PNG.<br>' +\
    '<div class="small_line_indent"></div>'


def paper(request):
    return render_to_response('examples/paper/index.html')


def e_coli(request, download_fname):
    return common_view('paper/', 'E. coli', 'e.coli', download_fname)


def h_sapiens(request, download_fname):
    return common_view('paper/', 'H. sapiens chr. 14', 'h.sapiens_chr14', download_fname)


def b_impatiens(request, download_fname):
    return common_view('paper/', 'B. impatiens', 'b.impatiens', download_fname)


def e_coli_sc(request):
    return report_view('', 'E. coli, single cell', 'e.coli-single-cell')

def e_coli_mc(request):
    return report_view('', 'E. coli, isolate', 'e.coli-isolate')

def e_coli_sc_download(request, download_fname):
    return download_report_view(download_fname)

def e_coli_mc_download(request, download_fname):
    return download_report_view(download_fname)

def e_coli_sc_icarus(request):
    return icarus_view('', 'E. coli, single cell', 'e.coli-single-cell')

def e_coli_mc_icarus(request, download_fname):
    return icarus_view('', 'E. coli, isolate', 'e.coli-isolate')

def e_coli_sc_icarus_alignment(request):
    return icarus_alignment_viewer_view('', 'E. coli, single cell', 'e.coli-single-cell')

def e_coli_mc_icarus_alignment(request):
    return icarus_alignment_viewer_view('', 'E. coli, isolate', 'e.coli-isolate')

def e_coli_sc_icarus_contig_size(request):
    return icarus_contig_size_viewer_view('', 'E. coli, single cell', 'e.coli-single-cell')

def e_coli_mc_icarus_contig_size(request):
    return icarus_contig_size_viewer_view('', 'E. coli, isolate', 'e.coli-isolate')


def report_view(dir_name, caption, slug_name, template_dir_name=None,
                html_template_name=None, data_set_name=None, title=None):
    template_dir_name = 'examples/' + (template_dir_name or dir_name)
    html_template_name = html_template_name or slug_name

    response_dict = dict(settings.TEMPLATE_ARGS_BY_DEFAULT)

    report_dict = get_report_response_dict(os.path.join(settings.FILES_DIRPATH, dir_name, slug_name))
    response_dict.update(report_dict)

    response_dict['caption'] = caption
    response_dict['title'] = title
    response_dict['hide_date'] = True

    response_dict['download_link'] = slug_name + '_quast_report.zip'
    response_dict['download_text'] = download_text
    response_dict['download'] = True

    response_dict['data_set'] = {
        'title': data_set_name,
    }

    return render_to_response(template_dir_name + html_template_name + '.html', response_dict)


def download_report_view(download_fname):
    download_fpath = os.path.join(settings.FILES_DOWNLOADS_DIRPATH, download_fname)

    if os.path.exists(download_fpath):
        wrapper = FileWrapper(open(download_fpath, 'r'))
        content_type = mimetypes.guess_type(download_fpath)[0]

        response = HttpResponse(wrapper, content_type=content_type)
        response['Content-Length'] = os.path.getsize(download_fpath)
        response['Content-Disposition'] = 'attachment; filename=' + smart_str(download_fname)

        return response
    else:
        raise Http404('File %s does not exist' % download_fname)


def icarus_view(dir_name, caption, slug_name, template_dir_name=None,
                html_template_name=None, data_set_name=None, title=None):
    response_dict = dict(settings.TEMPLATE_ARGS_BY_DEFAULT)
    report_dict = get_icarus_menu_response_dict(os.path.join(settings.FILES_DIRPATH, dir_name, slug_name))
    response_dict.update(report_dict)
    response_dict['hide_date'] = True
    response_dict['title'] = 'Icarus main menu'

    return render_to_response('icarus/icarus-menu.html', response_dict)


def icarus_alignment_viewer_view(dir_name, caption, slug_name, template_dir_name=None,
                html_template_name=None, data_set_name=None, title=None):
    response_dict = dict(settings.TEMPLATE_ARGS_BY_DEFAULT)
    report_dict = get_icarus_response_dict(os.path.join(settings.FILES_DIRPATH, dir_name, slug_name))
    response_dict.update(report_dict)
    response_dict['hide_date'] = True
    response_dict['title'] = 'Contig alignment viewer'

    return render_to_response('icarus/icarus-viewer.html', response_dict)


def icarus_contig_size_viewer_view(dir_name, caption, slug_name, template_dir_name=None,
                html_template_name=None, data_set_name=None, title=None):
    response_dict = dict(settings.TEMPLATE_ARGS_BY_DEFAULT)
    report_dict = get_icarus_response_dict(os.path.join(settings.FILES_DIRPATH, dir_name, slug_name), is_contig_size_plot=True)
    response_dict.update(report_dict)
    response_dict['hide_date'] = True
    response_dict['title'] = 'Contig size viewer'

    return render_to_response('icarus/icarus-viewer.html', response_dict)


__spades_on_gage_b__caption_template = '%s MiSeq SPAdes&nbsp;%s assemblies'
__spades_on_gage_b__title_template = __spades_on_gage_b__caption_template


def __spades_on_gage_b_data_sets__common(download_fname, name, spades_ver, is_scaf=False):
    slug = name.replace(' ', '').lower()

    if is_scaf:
        slug += '-scf'

    return common_view(
        dir_name='spades.' + spades_ver + '-on-gage.b-data-sets/',
        caption=__spades_on_gage_b__caption_template %
                (name.replace(' ', '&nbsp;') + (' (scaffolds)' if is_scaf else ''), spades_ver),
        slug_name=slug,
        download_fname=download_fname,
        template_dir_name='spades-on-gage.b-data-sets/',
        html_template_name='common_report',
        data_set_name=name,
        title=__spades_on_gage_b__title_template %
              (name + (' (scaffolds)' if is_scaf else ''), spades_ver))


def spades_on_gage_b_data_sets(request, spades_ver):
    return render_to_response('examples/spades-on-gage.b-data-sets/index.html', {'version': spades_ver})

def spades_on_gage_b_data_sets__b_cereus(request, download_fname, spades_ver, is_scaf=False):
    return __spades_on_gage_b_data_sets__common(download_fname, 'B. cereus', spades_ver, is_scaf)

def spades_on_gage_b_data_sets__m_abscessus(request, download_fname, spades_ver, is_scaf=False):
    return __spades_on_gage_b_data_sets__common(download_fname, 'M. abscessus', spades_ver, is_scaf)

def spades_on_gage_b_data_sets__r_sphaeroides(request, download_fname, spades_ver, is_scaf=False):
    return __spades_on_gage_b_data_sets__common(download_fname, 'R. sphaeroides', spades_ver, is_scaf)

def spades_on_gage_b_data_sets__v_cholerae(request, download_fname, spades_ver, is_scaf=False):
    return __spades_on_gage_b_data_sets__common(download_fname, 'V. cholerae', spades_ver, is_scaf)


def common_view(dir_name, caption, slug_name, download_fname, template_dir_name=None,
                html_template_name=None, data_set_name=None, title=None):
    template_dir_name = 'examples/' + (template_dir_name or dir_name)
    html_template_name = html_template_name or slug_name

    if download_fname:
        download_fpath = os.path.join(settings.FILES_DOWNLOADS_DIRPATH, download_fname)

        if os.path.exists(download_fpath):
          # if download_fname[-4:] == '.zip':
          #     mimetype = 'application/zip'
          # else:
          # mimetype = 'application/force-download'

          # f = FileWrapper(fpath)
          # response = HttpResponse(mimetype=mimetype)
          # response['Content-Disposition'] = 'attachment; filename=%s' % download_fname
          # response['X-Sendfile'] = download_fpath
          # response['Content-Length'] = 100
          # return response

            wrapper = FileWrapper(open(download_fpath, 'r'))
            content_type = mimetypes.guess_type(download_fpath)[0]

            response = HttpResponse(wrapper, content_type=content_type)
            response['Content-Length'] = os.path.getsize(download_fpath)
            response['Content-Disposition'] = 'attachment; filename=' + smart_str(download_fname)

            return response

        else:
            raise Http404('File %s does not exist' % download_fname)

    else:
        response_dict = dict(settings.TEMPLATE_ARGS_BY_DEFAULT)

        report_dict = get_report_response_dict(
            os.path.join(settings.FILES_DIRPATH, dir_name, slug_name))
        response_dict.update(report_dict)

        response_dict['caption'] = caption
        response_dict['title'] = title
        response_dict['hide_date'] = True

        response_dict['download_link'] = slug_name + '_quast_report.zip'
        response_dict['download_text'] = download_text

        response_dict['data_set'] = {
            'title': data_set_name,
        }

        return render_to_response(template_dir_name + html_template_name + '.html', response_dict)