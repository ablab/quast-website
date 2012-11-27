
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from quast_app import views

import logging
logger = logging.getLogger('quast')


urlpatterns = patterns('',
    url(r'^/?$', 'quast_app.views.index'),
    url(r'^example/?$', 'quast_app.views.example'),
    url(r'^manual_1\.3/?$', 'quast_app.views.manual'),
    url(r'^manual_1\.3\.html$', 'quast_app.views.manual'),
    url(r'^LICENSE$', 'quast_app.views.license'),

  # url(r'^report-scripts/(?P<script_name>[1-9a-z_\-]+.js)/?$', 'quast_app.views.report_scripts'),

    url(r'^ecoli/?$', 'quast_app.views.ecoli'),
    url(r'^benchmarking/?$', 'quast_app.views.benchmarking'),

#    url(r'^evaluate/?$', 'quast_app.views.evaluate'),

    url(r'^contigs-ajax-upload$', views.contigs_uploader.upload, name='contigs_ajax_upload'),
    url(r'^contigs-ajax-remove$', views.contigs_uploader.remove, name='contigs_ajax_remove'),
    url(r'^contigs-ajax-initialize-uploads$', views.contigs_uploader.initialize_uploads, name='contigs_ajax_initialize_uploads'),
    url(r'^contigs-ajax-remove-all$', views.contigs_uploader.remove_all, name='contigs_ajax_remove_all'),

    url(r'^reports/?$', 'quast_app.views.reports'),
    url(r'^report/(?P<report_id>.+)/?$', 'quast_app.views.report'),
    url(r'^download-report/(?P<report_id>.+)$', 'quast_app.views.download_report'),

    url(r'^404', 'django.views.generic.simple.direct_to_template', {'template': '404.html'}),
    url(r'^500', 'django.views.generic.simple.direct_to_template', {'template': '500.html'}),

    # Examples:
    # url(r'^$', 'quast_website.views.home', name='home'),
    # url(r'^quast_website/', include('quast_website.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()


#import object_tools
#object_tools.autodiscover()
#urlpatterns += patterns('',
#    (r'^object-tools/', include(object_tools.tools.urls)),
#)
