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

    url(r'^$', 'quast_app.views.index'),
    url(r'^latestreport/', 'quast_app.views.latest'),
    url(r'^assess/', 'quast_app.views.assess'),
    url(r'^manual$', 'quast_app.views.manual'),
    url(r'^manual\.html$', 'quast_app.views.manual'),

    url(r'^evaluate$', 'quast_app.views.evaluate'),
    url(r'^contigs-ajax-upload$', views.contigs_uploader, name="contigs_ajax_upload"),
    url(r'^reference-ajax-upload$', views.reference_uploader, name="reference_ajax_upload"),
    url(r'^genes-ajax-upload$', views.genes_uploader, name="genes_ajax_upload"),
    url(r'^operons-ajax-upload$', views.operons_uploader, name="operons_ajax_upload"),
    url(r'^report$', 'quast_app.views.evaluate_get_report'),
)

urlpatterns += staticfiles_urlpatterns()
