# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import redirect

import quast_app
admin.autodiscover()

from django.conf import settings
from django.conf.urls import include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView, RedirectView

from quast_app import views, login_views, example_reports_views, add_default_references

import logging
logger = logging.getLogger('quast')


urlpatterns = [
    url(r'^robots\.txt$', RedirectView.as_view(url='/static/robots.txt')),
    url(r'^sitemap\.xml$', RedirectView.as_view(url='/static/sitemap.xml')),
    url(r'^excanvas\.min\.js$', RedirectView.as_view(url='/static/flot/excanvas.min.js')),
    url(r'^favicon\.ico$', RedirectView.as_view(
        url=('/static/img/favicon_debug.ico' if settings.DEBUG else '/static/img/favicon.ico'))),

    url(r'^quast/$', quast_app.views.index),

    # open to update reference database
    # url(r'^quast/add_refs.*$', quast_app.add_default_references.add_refs),

    url(r'^quast/manual.*$', quast_app.views.manual),
    url(r'^quast/changes.*$', quast_app.views.changes),
    url(r'^quast/CHANGES.*$', quast_app.views.changes),
    url(r'^quast/manual_1\.3/?$', quast_app.views.manual),
    url(r'^quast/manual_1\.3\.html$', quast_app.views.manual),
    url(r'^quast/license.*$', quast_app.views.license),
    url(r'^quast/LICENSE.*$', quast_app.views.license),
    url(r'^quast/benchmarking/?$', quast_app.views.benchmarking),
    url(r'^quast/example/?$', quast_app.views.example),
    url(r'^quast/ecoli/?$', quast_app.views.idba),

    url(r'^quast/about.*', TemplateView.as_view(template_name='about.html')),
    url(r'^quast/contact.*', TemplateView.as_view(template_name='contact.html')),
    url(r'^quast/download.*', TemplateView.as_view(template_name='download.html')),
    url(r'^quast/help.*', TemplateView.as_view(template_name='help.html')),

    url(r'^quast/quast3/demo\.html$', RedirectView.as_view(url='/static/quast3/demo.html')),

    url(r'^quast/sample_data/report\.html$', quast_app.example_reports_views.sample_data),
    url(r'^quast/sample_data/?$', lambda _: redirect(quast_app.example_reports_views.sample_data)),
    url(r'^quast/sample_data/icarus\.html$', quast_app.example_reports_views.sample_data_icarus),
    url(r'^quast/sample_data/icarus_viewers/alignment_viewer*\.html$',
        quast_app.example_reports_views.sample_data_icarus_alignment),
    url(r'^quast/sample_data/icarus_viewers/contig_size_viewer*\.html$',
        quast_app.example_reports_views.sample_data_icarus_contig_size),
    url(r'^quast/sample_data/(?P<download_fname>.+)/?$', quast_app.example_reports_views.sample_data_download),

    url(r'^quast/sample_data_no_ref/report\.html$', quast_app.example_reports_views.sample_data_no_ref),
    url(r'^quast/sample_data_no_ref/?$', lambda _: redirect(quast_app.example_reports_views.sample_data_no_ref)),
    url(r'^quast/sample_data_no_ref/icarus\.html$', quast_app.example_reports_views.sample_data_no_ref_icarus),
    url(r'^quast/sample_data_no_ref/icarus_viewers/contig_size_viewer*\.html$',
        quast_app.example_reports_views.sample_data_no_ref_icarus_contig_size),
    url(r'^quast/sample_data_no_ref/(?P<download_fname>.+)/?$', quast_app.example_reports_views.sample_data_no_ref_download),

    url(r'^quast/e\.coli-single-cell/report\.html$', quast_app.example_reports_views.e_coli_sc),
    url(r'^quast/e\.coli-single-cell/?$', lambda _: redirect(quast_app.example_reports_views.e_coli_sc)),
    url(r'^quast/e\.coli-single-cell/icarus\.html$', quast_app.example_reports_views.e_coli_sc_icarus),
    url(r'^quast/e\.coli-single-cell/icarus_viewers/alignment_viewer*\.html$', quast_app.example_reports_views.e_coli_sc_icarus_alignment),
    url(r'^quast/e\.coli-single-cell/icarus_viewers/contig_size_viewer*\.html$', quast_app.example_reports_views.e_coli_sc_icarus_contig_size),
    url(r'^quast/e\.coli-single-cell/(?P<download_fname>.+)/?$', quast_app.example_reports_views.e_coli_sc_download),

    url(r'^quast/e\.coli-isolate/report\.html$', quast_app.example_reports_views.e_coli_mc),
    url(r'^quast/e\.coli-isolate/?$', lambda _: redirect(quast_app.example_reports_views.e_coli_mc)),
    url(r'^quast/e\.coli-isolate/icarus\.html$', quast_app.example_reports_views.e_coli_mc_icarus),
    url(r'^quast/e\.coli-isolate/icarus_viewers/alignment_viewer*\.html$', quast_app.example_reports_views.e_coli_mc_icarus_alignment),
    url(r'^quast/e\.coli-isolate/icarus_viewers/contig_size_viewer*\.html$', quast_app.example_reports_views.e_coli_mc_icarus_contig_size),
    url(r'^quast/e\.coli-isolate/(?P<download_fname>.+)/?$', quast_app.example_reports_views.e_coli_mc_download),

    url(r'^quast/reports/(?P<link>.+)/icarus_viewers/alignment_viewer*\.html$', quast_app.views.icarus_alignment_viewer),
    url(r'^quast/reports/(?P<link>.+)/icarus_viewers/contig_size_viewer*\.html$', quast_app.views.icarus_contig_size_viewer),

    url(r'^quast/paper/$', quast_app.example_reports_views.paper),
    url(r'^quast/paper/e\.coli/(?P<download_fname>.+)?/?$', quast_app.example_reports_views.e_coli),
    url(r'^quast/paper/b\.impatiens/(?P<download_fname>.+)?/?$', quast_app.example_reports_views.b_impatiens),
    url(r'^quast/paper/h\.sapiens_chr14/(?P<download_fname>.+)?/?$', quast_app.example_reports_views.h_sapiens),

    url(r'^quast/paper/h.sapiens_chr14/download/?$',
        RedirectView.as_view(url='/static/data_sets/h.sapiens_chr14/h_sapiens_chr14_quast_report.zip'),
        name='h_sapiens_quast_report'),

    url(r'^quast/contigs-ajax-upload$', views.contigs_uploader.upload, name='contigs_ajax_upload'),
    url(r'^quast/contigs-ajax-remove$', views.contigs_uploader.remove, name='contigs_ajax_remove'),
    url(r'^quast/contigs-ajax-initialize-uploads$', views.contigs_uploader.initialize_uploads, name='contigs_ajax_initialize_uploads'),
    url(r'^quast/contigs-ajax-remove-all$', views.contigs_uploader.remove_all, name='contigs_ajax_remove_all'),
    url(r'^quast/ajax-delete-session$', views.delete_session, name='ajax_delete_session'),

    url(r'^quast/reports/?$', quast_app.views.reports),

    url(r'^quast/reports/download/(?P<link>.+)/?$', quast_app.views.download_report),
    url(r'^quast/reports/(?P<link>.+)/report\.html$', quast_app.views.report),
    url(r'^quast/reports/(?P<link>.+)/icarus\.html$', quast_app.views.icarus),
    url(r'^quast/reports/(?P<link>.+)/icarus_viewers/alignment_viewer\.html$', quast_app.views.icarus_alignment_viewer),
    url(r'^quast/reports/(?P<link>.+)/icarus_viewers/contig_size_viewer\.html$', quast_app.views.icarus_contig_size_viewer),
    url(r'^quast/reports/(?P<link>.+)/?$', lambda _, link: redirect('quast_app.views.report', link=link)),

    url(r'^quast/data-sets/(?P<data_set_id>.+)_(?P<what>.+)(?P<file_ext>\..+)$',
        views.download_data_set, name='download_data_set'),
    url(r'^quast/data-sets/(?P<data_set_id>.+)(?P<file_ext>\..+)$',
        views.download_data_set, {'what': 'reference'}, name='download_data_set'),

    url(r'^quast/reorder-report-columns$', quast_app.views.reorder_report_columns_ajax),

    url(r'^quast/500', TemplateView.as_view(template_name='500.html')),
    url(r'^quast/404', TemplateView.as_view(template_name='404.html')),

    url(r'^quast/ask_password', quast_app.login_views.ask_password, name='ask_password_link'),
    url(r'^quast/login', quast_app.login_views.login, name='login_link'),

    url(r'^quast/admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^quast/admin/', include(admin.site.urls)),
]

for ver in ('2.5', '3.0'):
    urlpatterns.append(url(r'^quast/spades.' + ver + '-on-gage.b-data-sets/$',
            quast_app.example_reports_views.spades_on_gage_b_data_sets,
            {'spades_ver': ver}))

    for d_set_slug in ['b.cereus', 'm.abscessus', 'r.sphaeroides', 'v.cholerae']:
        urlpatterns.extend([
            url(r'^quast/spades.' + ver + '-on-gage.b-data-sets/' + d_set_slug + '/(?P<download_fname>.+)?/?$',
                'quast_app.example_reports_views.spades_on_gage_b_data_sets__' + d_set_slug.replace('.', '_'),
                {'is_scaf': False, 'spades_ver': ver}),

            url(r'^quast/spades.' + ver + '-on-gage.b-data-sets/' + d_set_slug + '-scaffolds/(?P<download_fname>.+)?/?$',
                'quast_app.example_reports_views.spades_on_gage_b_data_sets__' + d_set_slug.replace('.', '_'),
                {'is_scaf': True, 'spades_ver': ver}),
        ])

urlpatterns += staticfiles_urlpatterns()

#import object_tools
#object_tools.autodiscover()
#urlpatterns += patterns('',
#    (r'^quast/object-tools/', include(object_tools.tools.urls)),
#)
