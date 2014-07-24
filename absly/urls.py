from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from app.views import *
from steps.views import *
from talk.views import *

import analytics, logging

from app.api import CanvasBlockList, CanvasBlockDetail, CanvasBlockItemList, CanvasBlockItemDetail
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

analytics.init('kt58pb0ynb', flush_at=1)

urlpatterns = patterns('',
    # Examples:
    url(r'^oauth2callback/$', auth_return, name='oauth2-callback'),
    url(r'^ga-config/$', GAConfigView.as_view(), name='ga-config-view'),
    url(r'^ga/config/account/$', GAWeboptsView.as_view(), name='ga-config-account'),
    url(r'^ga/config/webprops/$', GAProfileView.as_view(), name='ga-config-webprops'),
    url(r'^ga/config/profile/$', GAProfileCompletedView.as_view(), name='ga-config-profile'),
    url(r'^ga/config/funnel/$', GAFunnelConfigAjaxView.as_view(), name='ga-config-funnel'),
    url(r'^ga-funnel/$', GAFunnelView.as_view(), name='ga-funnel-view'),


    url(r'^$', DashboardView.as_view(), name='home'),

    url(r'^accounts/', include('registration.backends.default.urls')),

    url(r'^dashboard/$', DashboardView.as_view(), name='dashboard'),
    url(r'^ng-canvas/$', TemplateView.as_view(template_name='ng-canvas.html'), name='ng-canvas'),
    url(r'^canvas/$', CanvasView.as_view(), name='canvas'),
    url(r'^canvas/element/add/$', CreateElementAjaxView.as_view(), name='canvas-create'),

    url(r'^canvas/block/new/form/', CanvasElementGetFormView.as_view(), name='canvas-get-new-form'),
    url(r'^canvas/change/level/log/', CanvasLogFormView.as_view(), name='canvas-get-log-form'),

    url(r'^update/top/statistics/', UpdateTopStatisticsView.as_view(), name='update-top-statistics-view'),

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
    url(r"^summary/del/block/(?P<pk>\d+)/$", SummaryDeleteBlock.as_view(), name='summary-del-block'),

    url(r'^summary/cb/block/$', SummaryCrunchBaseBlockView.as_view(), name='summary-cb-block'),
    url(r'^summary/angellist/block/$', SummaryAngelListBlockView.as_view(), name='summary-angellist-block'),
    url(r'^summary/linkedin/block/$', SummaryLinkedInBlockView.as_view(), name='summary-linkedin-block'),
    url(r'^summary/text/block/$', SummaryTextBlockView.as_view(), name='summary-text-block'),
    url(r'^summary/link/block/$', SummaryLinkBlockView.as_view(), name='summary-link-block'),
    url(r'^summary/image/block/$', SummaryImageBlockView.as_view(), name='summary-image-block'),

    url(r'^summary/public/(?P<hash>[\w\d]+)/$', SummaryPubView.as_view(), name='summary-public'),

    url(r'^summary/$', ExecutiveSummaryView.as_view(), name='summary'),
    url(r'^summary/snapshot/$', SnapshotView.as_view(), name='snapshot-ajax-view'),
    url(r'^summary/(?P<pk>\d+)/$', ExecutiveSummaryItemView.as_view(), name='summary-group'),
    url(r'^summary/item/(?P<pk>\d+)/$', ExecutiveSummaryItemUpdateView.as_view(), name='summary-item-update'),

    url(r'^steps/$', StepsView.as_view(), name='steps'),
    url(r'^steps/sort/$', StepsSortView.as_view(), name='steps-sort'),
    url(r'^steps/del/(?P<pk>\d+)/$', StepDelView.as_view(), name='step-del-view'),
    url(r'^steps/done/(?P<pk>\d+)/$', StepDoneView.as_view(), name='step-done-view'),
    url(r'^steps/add/$', StepAddView.as_view(), name='step-add-view'),
    url(r'^steps/edit/(?P<pk>\d+)/$', StepEditView.as_view(), name='step-edit-view'),
    url(r'^steps/recomendation/$', RecomendationView.as_view(), name='steps-recomendation'),

    url(r'^metrics/$', MetricsView.as_view(), name='metrics'),
    url(r'^strategy/$', StrategyView.as_view(), name='strategy'),
    url(r'^communicate/$', EventsListView.as_view(), name='events'),
    url(r'^communicate/(?P<pk>\d+)/$', EventsGroupListView.as_view(), name='communicate-group'),
    url(r'^events/delete/(?P<pk>\d+)/$', EventDeleteView.as_view(), name='event_delete'),
    # url(r'^absly/', include('absly.foo.urls')),

    # talk
    url(r'^talk/requests/$', InvestorsRequestsView.as_view(), name='investors-requests'),
    url(r'^talk/posts/$', PostsView.as_view(), name='posts-view'),
    url(r'^talk/posts/(?P<pk>\d+)/$', PostDetailView.as_view(), name='post-detail-view'),
    url(r'^talk/news/$', NewsView.as_view(), name='news-view'),
    url(r'^talk/system/$', SystemView.as_view(), name='system-notifications-view'),
    url(r'^talk/system/(?P<pk>\d+)/$', SystemDetailView.as_view(), name='system-notification-detail-view'),


    url(r'^new/$', CreateProjectView.as_view(), name='new-project'),
    url(r'^personal/$', PersonalDataView.as_view(), name='personal-data-view'),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
