from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()
from quast_app import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'quast_website.views.home', name='home'),
    # url(r'^quast_website/', include('quast_website.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    url(r'^/?$', 'quast_app.views.index'),
    url(r'^example/?', 'quast_app.views.example'),
#    url(r'^assess/', 'quast_app.views.assess'),
    url(r'^manual/?$', 'quast_app.views.manual'),
    url(r'^LICENSE$', 'quast_app.views.license'),
    url(r'^manual\.html$', 'quast_app.views.manual'),

    url(r'^evaluate/?$', 'quast_app.views.evaluate'),
    url(r'^evaluate/run/?$', 'quast_app.views.evaluate'),
    url(r'^contigs-ajax-upload$', views.contigs_uploader, name='contigs_ajax_upload'),
    url(r'^contigs-ajax-remove$', views.contigs_uploader.remove, name='contigs_ajax_remove'),
    url(r'^contigs-ajax-initialize-uploads$', views.contigs_uploader.initialize_uploads, name='contigs_ajax_initialize_uploads'),

    url(r'^report/(?P<report_id>.+)/?$', 'quast_app.views.report'),

#   url(r'^reference-ajax-upload$', views.reference_uploader, name="reference_ajax_upload"),
#   url(r'^genes-ajax-upload$', views.genes_uploader, name="genes_ajax_upload"),
#   url(r'^operons-ajax-upload$', views.operons_uploader, name="operons_ajax_upload"),

    url(r'^do_stuff$', 'quast_app.do_stuff.do_stuff')
)

urlpatterns += staticfiles_urlpatterns()

