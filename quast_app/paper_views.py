from django.conf import settings
from views_report import get_report_response_dict
from django.shortcuts import render_to_response


download_text = '' +\
  'Text, TSV and Latex versions<br>' +\
  'of the table, plots in PNG.<br>' +\
  '<div class="small_line_indent"></div>'



def e_coli(request):
    report_response_dict = get_report_response_dict(
        settings.E_COLI_DIRPATH,
        caption='E. coli',
        )
    response_dict = dict(report_response_dict.items() + settings.TEMPLATE_ARGS_BY_DEFAULT.items())

    response_dict['download'] = True
    response_dict['downloadLink'] = 'e.coli/download/'
    response_dict['downloadText'] = download_text

    return render_to_response('paper/e.coli.html', response_dict)


def h_sapiens(request):
    report_response_dict = get_report_response_dict(
        settings.H_SAPIENS_DIRPATH,
        caption='H. sapiens, chr. 14',
    )
    response_dict = dict(report_response_dict.items() + settings.TEMPLATE_ARGS_BY_DEFAULT.items())

    response_dict['download'] = True
    response_dict['downloadLink'] = 'h.sapiens_chr14/download/'
    response_dict['downloadText'] = download_text

    return render_to_response('paper/h.sapiens_chr14.html', response_dict)


def b_impatiens(request):
    report_response_dict = get_report_response_dict(
        settings.B_IMPATIENS_DIRPATH,
        caption='B. impatiens',
        )
    response_dict = dict(report_response_dict.items() + settings.TEMPLATE_ARGS_BY_DEFAULT.items())

    response_dict['download'] = True
    response_dict['downloadLink'] = 'b.impatiens/download/'
    response_dict['downloadText'] = download_text

    return render_to_response('paper/b.impatiens.html', response_dict)




#no reference is available at the moment. Estimated size is 250 Mb.
