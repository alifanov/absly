from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from app.views import EventsListView, EventDeleteView, StrategyView, StepsView, MetricsView, ExecutiveSummaryView,\
CanvasView, DashboardView, ExecutiveSummaryItemView, ExecutiveSummaryItemUpdateView, EventsGroupListView
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', TemplateView.as_view(
        template_name='index.html'
    ), name='home'),

    url(r'^accounts/', include('registration.backends.default.urls')),

    url(r'^dashboard/$', DashboardView.as_view(), name='dashboard'),
    url(r'^canvas/$', CanvasView.as_view(), name='canvas'),

    url(r'^summary/$', ExecutiveSummaryView.as_view(), name='summary'),
    url(r'^summary/(?P<pk>\d+)/$', ExecutiveSummaryItemView.as_view(), name='summary-group'),
    url(r'^summary/item/(?P<pk>\d+)/$', ExecutiveSummaryItemUpdateView.as_view(), name='summary-item-update'),

    url(r'^metrics/$', MetricsView.as_view(), name='metrics'),
    url(r'^strategy/$', StrategyView.as_view(), name='strategy'),
    url(r'^steps/$', StepsView.as_view(), name='steps'),
    url(r'^communicate/$', EventsListView.as_view(), name='events'),
    url(r'^communicate/(?P<pk>\d+)/$', EventsGroupListView.as_view(), name='communicate-group'),
    url(r'^events/delete/(?P<pk>\d+)/$', EventDeleteView.as_view(), name='event_delete'),
    # url(r'^absly/', include('absly.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
