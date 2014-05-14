from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from app.views import EventsListView, EventDeleteView
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', TemplateView.as_view(
        template_name='index.html'
    ), name='home'),

    url(r'^strategy/$', TemplateView.as_view(template_name='strategy.html'), name='strategy'),
    url(r'^communicate/$', EventsListView.as_view(), name='events'),
    url(r'^events/delete/(?P<pk>\d+)/$', EventDeleteView.as_view(), name='event_delete'),
    # url(r'^absly/', include('absly.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
