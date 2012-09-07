
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from quast_app import views

urlpatterns = patterns('',
    url(r'^/?$', 'quast_app.views.index'),
    url(r'^example/?$', 'quast_app.views.example'),
    url(r'^manual/?$', 'quast_app.views.manual'),
    url(r'^LICENSE$', 'quast_app.views.license'),
    url(r'^manual\.html$', 'quast_app.views.manual'),

    url(r'^ecoli/?$', 'quast_app.views.ecoli'),

    url(r'^evaluate/?$', 'quast_app.views.evaluate'),
    url(r'^evaluate/?$', 'quast_app.views.evaluate'),

    url(r'^contigs-ajax-upload$', views.contigs_uploader, name='contigs_ajax_upload'),
    url(r'^contigs-ajax-remove$', views.contigs_uploader.remove, name='contigs_ajax_remove'),
    url(r'^contigs-ajax-initialize-uploads$', views.contigs_uploader.initialize_uploads, name='contigs_ajax_initialize_uploads'),

    url(r'^reports/?$', 'quast_app.views.reports'),
    url(r'^report/(?P<report_id>.+)/?$', 'quast_app.views.report'),

    url(r'^do_stuff/?$', 'quast_app.do_stuff.do_stuff'),

    # Examples:
    # url(r'^$', 'quast_website.views.home', name='home'),
    # url(r'^quast_website/', include('quast_website.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()

