from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from app.views import *

from app.api import CanvasBlockList, CanvasBlockDetail, CanvasBlockItemList, CanvasBlockItemDetail
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^oauth2callback/$', auth_return, name='oauth2-callback'),
    url(r'^ga-config/$', GAConfigView.as_view(), name='ga-config-view'),
    url(r'^ga/config/account/$', GAWeboptsView.as_view(), name='ga-config-account'),
    url(r'^ga-funnel/$', GAFunnelView.as_view(), name='ga-funnel-view'),


    url(r'^$', DashboardView.as_view(), name='home'),

    url(r'^accounts/', include('registration.backends.default.urls')),

    url(r'^dashboard/$', DashboardView.as_view(), name='dashboard'),
    url(r'^canvas/$', TemplateView.as_view(template_name='ng-canvas.html'), name='ng-canvas'),
    url(r'^ng-canvas/$', CanvasView.as_view(), name='canvas'),
    url(r'^canvas/element/add/$', CreateElementAjaxView.as_view(), name='canvas-create'),

    url(r'^parse/json/$', ParseCanvasDataView.as_view(), name='parse-json'),

    url(r'^partners/json/$', PartnersJSONView.as_view(), name='partners-json'),
    url(r'^segments/json/$', SegmentsJSONView.as_view(), name='segments-json'),
    url(r'^values/json/$', ValuePropositionJSONView.as_view(), name='values-json'),
    url(r'^revenue/json/$', RevenueStreamsJSONView.as_view(), name='revenue-json'),
    url(r'^costs/json/$', CostStructureJSONView.as_view(), name='costs-json'),
    url(r'^activities/json/$', KeyActivitiesJSONView.as_view(), name='activities-json'),
    url(r'^resources/json/$', KeyResourseJSONView.as_view(), name='resources-json'),
    url(r'^channels/json/$', ChannelsJSONView.as_view(), name='channels-json'),
    url(r'^relations/json/$', CustomerRelationshipJSONView.as_view(), name='relations-json'),

    url(r'^api/canvas/$', CanvasBlockList.as_view(), name='canvas-block-list'),
    url(r'^api/canvas/(?P<pk>\d+)/$', CanvasBlockDetail.as_view(), name='canvas-block-detail'),
    url(r'^api/canvas/item/$', CanvasBlockItemList.as_view(), name='canvas-block-item-list'),
    url(r'^api/canvas/item/(?P<pk>\d+)/$', CanvasBlockItemDetail.as_view(), name='canvas-block-item-detail'),

    url(r"^summary/update/block/(?P<pk>\d+)/$", SummaryUpdateBlockView.as_view(), name='summary-update-block'),

    url(r'^summary/linkedin/block/$', SummaryLinkedInBlockView.as_view(), name='summary-linkedin-block'),
    url(r'^summary/text/block/$', SummaryTextBlockView.as_view(), name='summary-text-block'),
    url(r'^summary/link/block/$', SummaryLinkBlockView.as_view(), name='summary-link-block'),
    url(r'^summary/image/block/$', SummaryImageBlockView.as_view(), name='summary-image-block'),

    url(r'^summary/public/(?P<md5>[\w\d]+)/(?P<pk>\d+)/$', SummaryPubView.as_view(), name='summary-public'),
    url(r'^summary/public/(?P<md5>[\w\d]+)/(?P<pk>\d+)/pdf/$', SummaryPDFView.as_view(), name='summary-public-pdf'),

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
