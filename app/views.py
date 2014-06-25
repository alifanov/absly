#coding: utf-8
# Create your views here.
from app.models import News, NewsGroup, GAProfile
from django.views.generic import ListView, View, TemplateView, DetailView, UpdateView, CreateView
from django.http import HttpResponse
from django.shortcuts import redirect
import arrow, logging
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_exempt

from app.models import SummaryGroup, SummaryItem, NewsGroup, CanvasBlock, CanvasBlockItem, CanvasBlockItemParameter, \
    CanvasBlockItemParameterValue
from app.forms import SummaryItemForm
import json, os
import httplib2

from apiclient.discovery import build
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from app.models import CredentialsModel
from django.conf import settings
from oauth2client import xsrfutil
from oauth2client.client import flow_from_clientsecrets
from oauth2client.django_orm import Storage

# OAuth2.0 process
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), '..','absly', 'client_secrets.json')

FLOW = flow_from_clientsecrets(
    CLIENT_SECRETS,
  scope='https://www.googleapis.com/auth/analytics.readonly',
    redirect_uri='http://absly.progernachas.ru/oauth2callback')

@login_required
def auth_return(request):
  if not xsrfutil.validate_token(settings.SECRET_KEY, request.REQUEST['state'],
                                 request.user):
    return  HttpResponseBadRequest()
  credential = FLOW.step2_exchange(request.REQUEST)
  storage = Storage(CredentialsModel, 'id', request.user, 'credential')
  storage.put(credential)
  return HttpResponseRedirect("/ga/")

class GAFunnelView(TemplateView):
    credentials = None
    template_name = 'ga-funnel.html'

    def get(self, request, *args, **kwargs):
        storage = Storage(CredentialsModel, 'id', self.request.user, 'credential')
        self.credential = storage.get()
        if self.credential is None or self.credential.invalid == True:
            return redirect(reverse('ga-config-view'))
        else:
            return super(GAFunnelView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):


    def get_context_data(self, **kwargs):
        ctx = super(GAFunnelView, self).get_context_data(**kwargs)
        http = httplib2.Http()
        http = self.credential.authorize(http)
        service = build("analytics", "v3", http=http)

        ga_profile = GAProfile.objects.get(user=self.request.user)
        ga_users = service.data().ga().get(
            ids='ga:{}'.format(ga_profile.profile_id),
            start_date='2014-06-01',
            end_date='2014-06-24',
            metrics='ga:users'
        ).execute()
        if ga_users.get('rows'):
            ctx['ga_users'] = ga_users.get('rows')[0][0]

        ga_pages = service.data().ga().get(
            ids='ga:{}'.format(ga_profile.profile_id),
            start_date='2014-06-01',
            end_date='2014-06-24',
            metrics='ga:sessions',
            dimensions='ga:pagePath',
            max_results=25
        ).execute()
        ctx['ga_pages'] = [p[0] for p in ga_pages.get('rows')]

        ga_events_categories = service.data().ga().get(
            ids='ga:{}'.format(ga_profile.profile_id),
            start_date='2014-06-01',
            end_date='2014-06-24',
            metrics='ga:sessions',
            dimensions='ga:eventCategory',
            max_results=25
        ).execute()
        ctx['ga_events_categories'] = [p[0] for p in ga_events_categories.get('rows')]

        ga_events_actions = service.data().ga().get(
            ids='ga:{}'.format(ga_profile.profile_id),
            start_date='2014-06-01',
            end_date='2014-06-24',
            metrics='ga:sessions',
            dimensions='ga:eventAction',
            max_results=25
        ).execute()
        ctx['ga_events_actions'] = [p[0] for p in ga_events_actions.get('rows')]

        ga_events_labels = service.data().ga().get(
            ids='ga:{}'.format(ga_profile.profile_id),
            start_date='2014-06-01',
            end_date='2014-06-24',
            metrics='ga:sessions',
            dimensions='ga:eventLabel',
            max_results=25
        ).execute()
        ctx['ga_events_labels'] = [p[0] for p in ga_events_labels.get('rows')]

        return ctx

class GAConfigView(TemplateView):
    credentials = None
    template_name = 'ga.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(GAConfigView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(GAConfigView, self).get_context_data(**kwargs)
        storage = Storage(CredentialsModel, 'id', self.request.user, 'credential')
        self.credential = storage.get()
        if self.credential is None or self.credential.invalid == True:
            FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY,
                                                       self.request.user)
            authorize_url = FLOW.step1_get_authorize_url()
            ctx['auth_url'] = authorize_url
        else:

            http = httplib2.Http()
            http = self.credential.authorize(http)
            service = build("analytics", "v3", http=http)
            accounts = service.management().accounts().list().execute()

            accounts_config = []
            for acc in accounts.get('items'):
                accounts_config.append((acc.get('id'), acc.get('name')))
            ctx['accounts'] = accounts_config
            if self.request.GET.get('account'):
                wps = service.management().webproperties().list(accountId=self.request.GET.get('account')).execute()
                webprops_config = []
                for wp in wps.get('items'):
                    webprops_config.append((wp.get('id'), wp.get('name')))
                ctx['webprops'] = webprops_config
                ctx['account'] = self.request.GET.get('account')
            if self.request.GET.get('webprop'):
                profiles = service.management().profiles().list(
                    accountId=self.request.GET.get('account'),
                    webPropertyId=self.request.GET.get('webprop')
                ).execute()
                if profiles.get('totalResults') > 0:
                    profiles_config = []
                    for pro in profiles.get('items'):
                        profiles_config.append((pro.get('id'), pro.get('name')))
                    ctx['profiles'] = profiles_config
                else:
                    ctx['profiles_error'] = u'Нет данных'
                    ctx['webprop'] = self.request.GET.get('webprop')
            if self.request.GET.get('profile'):
                ga_profile = None
                if GAProfile.objects.filter(user=self.request.user).exists():
                    ga_profile = GAProfile.objects.get(user=self.request.user)
                    ga_profile.account_id = self.request.GET.get('account')
                    ga_profile.webproperty_id = self.request.GET.get('webprop')
                    ga_profile.profile_id = self.request.GET.get('profile')
                else:
                    ga_profile = GAProfile(
                        user=self.request.user,
                        account_id = self.request.GET.get('account'),
                        webproperty_id = self.request.GET.get('webprop'),
                        profile_id = self.request.GET.get('profile'),
                    )
                ga_profile.save()
                ctx['account'] = self.request.GET.get('account')

            # data = profile_config
            # data = service.data().ga().get(
            #     start_date='2014-01-01',
            #     end_date='2014-06-18',
            #     ids='ga:82650359',
            #     metrics='ga:sessions'
            # ).execute()
            # ctx['data'] = data
        return ctx

@login_required
def ga_view(request):
    data = []
    storage = Storage(CredentialsModel, 'id', request.user, 'credential')
    credential = storage.get()
    if credential is None or credential.invalid == True:
        FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY,
                                                   request.user)
        authorize_url = FLOW.step1_get_authorize_url()
        return HttpResponseRedirect(authorize_url)
    else:
        http = httplib2.Http()
        http = credential.authorize(http)
        service = build("analytics", "v3", http=http)
        accounts = service.management().accounts().list().execute()
        data = accounts
        data = service.data().ga().get(
            start_date='2014-01-01',
            end_date='2014-06-18',
            ids='ga:82650359',
            metrics='ga:sessions'
        ).execute()

    return render_to_response('ga.html', {
                'data': data,
                })

class AjaxableResponseMixin(object):
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """
    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
#        if self.request.is_ajax():
        return self.render_to_json_response(form.errors, status=400)
#        else:
#            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
#        response = super(AjaxableResponseMixin, self).form_valid(form)
#        if self.request.is_ajax():
        self.object = form.save()
        data = {
            'pk': self.object.pk,
            }
        return self.render_to_json_response(data)
#        else:
#            return response

class ParseCanvasDataView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(ParseCanvasDataView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.POST:
            if request.POST.get('data'):
                data = request.POST.get('data')
                data = json.loads(data)
                for v in data:
                    if 'deleted' in v:
                        CanvasBlockItem.objects.filter(pk=v['deleted']).delete()
                    block = CanvasBlock.objects.get(name=v['name'])
                    for ii in v['items']:
                        segment = None
                        if 'segment' in ii:
                            segment = CanvasBlockItem.objects.get(pk=ii['segment']['pk'])
                        element = None
                        if 'pk' in ii and CanvasBlockItem.objects.filter(pk=ii['pk']).exists():
                            element = CanvasBlockItem.objects.get(pk=ii['pk'])
                            element.level = int(ii['level'])
                            element.name = ii['name']
                            element.segment = segment
                            element.save()
                        else:
                            element = CanvasBlockItem.objects.create(
                                name = ii['name'],
                                block = block,
                                level = int(ii['level']),
                                segment = segment
                            )

                        if 'levels' in ii:
                            element.updated_to_1_log = ii['levels'][1]['log']
                            element.updated_to_2_log = ii['levels'][2]['log']
                            element.updated_to_3_log = ii['levels'][3]['log']
                            element.save()

                        if 'params' in ii and ii['params']:
                            element.params_values.clear()
                            for pk,pv in ii['params'].items():
                                param = CanvasBlockItemParameter.objects.get(name=pk)
                                value = CanvasBlockItemParameterValue.objects.get(
                                    name=pv,
                                    parameter=param
                                )
                                value.elements.add(element)

        return HttpResponse('OK')

class CanvasBlockItenJSONMixin(object):
    def get(self, request, *args, **kwargs):
        ra = {'content_type': 'application/json'}
        partners_block = CanvasBlock.objects.get(name=self.name)
        qs = partners_block.params.all()
        items = partners_block.elements.all()
        data = {'name': partners_block.name,
                'questions': [{'q': q.name, 'ans': [a.name for a in q.values.all()]} for q in qs], 'items': []}
        for i in items:
            toadd_item = {
                'pk': i.pk,
                'level': i.level,
                'levels': [
                    {
                        'name': u'Гипотеза',
                        'log': u''
                    },
                    {
                        'name': u'Проверено фактами',
                        'log': i.updated_to_1_log
                    },
                    {
                        'name': u'Проверено действиями',
                        'log': i.updated_to_2_log
                    },
                    {
                        'name': u'Проверено деньгами',
                        'log': i.updated_to_3_log
                    },
                ],
                'name': i.name,
                'params': dict([[p.parameter.name, p.name] for p in i.params_values.all()])
            }
            if i.segment:
                toadd_item['segment'] = {
                    'pk': i.segment.pk,
                    'name': i.segment.name,
                    'level': i.segment.level,
                    'levels': [
                        {
                            'name': u'Гипотеза',
                            'log': u''
                        },
                        {
                            'name': u'Проверено фактами',
                            'log': i.segment.updated_to_1_log
                        },
                        {
                            'name': u'Проверено действиями',
                            'log': i.segment.updated_to_2_log
                        },
                        {
                            'name': u'Проверено деньгами',
                            'log': i.segment.updated_to_3_log
                        },
                    ],
                    'params': {}
                }
            data['items'].append(toadd_item)
        return HttpResponse(json.dumps(data), **ra)

class PartnersJSONView(CanvasBlockItenJSONMixin, View):
    name = 'Key Partners'

class SegmentsJSONView(CanvasBlockItenJSONMixin, View):
    name = 'Customer Segments'

class ValuePropositionJSONView(CanvasBlockItenJSONMixin, View):
    name = 'Value Proposition'

class KeyActivitiesJSONView(CanvasBlockItenJSONMixin, View):
    name = 'Key Activities'

class KeyResourseJSONView(CanvasBlockItenJSONMixin, View):
    name = 'Key Resources'

class ChannelsJSONView(CanvasBlockItenJSONMixin, View):
    name = 'Channels'

class CustomerRelationshipJSONView(CanvasBlockItenJSONMixin, View):
    name = 'Customer Relationship'

class CostStructureJSONView(CanvasBlockItenJSONMixin, View):
    name = 'Cost Structure'

class RevenueStreamsJSONView(CanvasBlockItenJSONMixin, View):
    name = 'Revenue Streams'

class CreateElementAjaxView(AjaxableResponseMixin, CreateView):
    model = CanvasBlockItem

class LeftMenuMixin(object):
    def get_context_data(self, **kwargs):
        ctx = super(LeftMenuMixin, self).get_context_data(**kwargs)
        ctx['summary_groups'] = SummaryGroup.objects.order_by('order')
        ctx['news_groups'] = NewsGroup.objects.all()
        return ctx

class DashboardView(LeftMenuMixin, TemplateView):
    template_name = 'dashboard.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(DashboardView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(DashboardView, self).get_context_data(**kwargs)
        ctx['active'] = 'canvas'
        return ctx


class CanvasView(LeftMenuMixin, TemplateView):
    template_name = 'canvas.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(CanvasView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(CanvasView, self).get_context_data(**kwargs)
        ctx['active'] = 'canvas'
        ctx['cse'] = CanvasBlock.objects.get(slug='customer-segments')
        ctx['vp'] = CanvasBlock.objects.get(slug='value-proposition')
        return ctx

class ExecutiveSummaryView(LeftMenuMixin, ListView):
    template_name = 'summary_list.html'
    model = SummaryGroup
    context_object_name = 'sgs'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ExecutiveSummaryView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(ExecutiveSummaryView, self).get_context_data(**kwargs)
        ctx['active'] = 'summary'
        return ctx

class ExecutiveSummaryItemView(LeftMenuMixin, DetailView):
    template_name = 'summary.html'
    model = SummaryGroup
    context_object_name = 'sg'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ExecutiveSummaryItemView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(ExecutiveSummaryItemView, self).get_context_data(**kwargs)
        ctx['active'] = 'summary'
        return ctx

class ExecutiveSummaryItemUpdateView(AjaxableResponseMixin, LeftMenuMixin, UpdateView):
#    template_name = 'summaryitem_form.html'
    model = SummaryItem
    form_class = SummaryItemForm
#    exclude = ['name','group', 'public']

class GoogleAnalyticsView(LeftMenuMixin, TemplateView):
    template_name = 'ga.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(GoogleAnalyticsView, self).dispatch(request, *args, **kwargs)

class MetricsView(LeftMenuMixin, TemplateView):
    template_name = 'metrics.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(MetricsView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(MetricsView, self).get_context_data(**kwargs)
        ctx['active'] = 'metrics'
        return ctx

class StepsView(LeftMenuMixin, TemplateView):
    template_name = 'steps.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(StepsView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(StepsView, self).get_context_data(**kwargs)
        ctx['active'] = 'steps'
        return ctx

class StrategyView(LeftMenuMixin, TemplateView):
    template_name = 'strategy.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(StrategyView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(StrategyView, self).get_context_data(**kwargs)
        ctx['active'] = 'strategy'
        return ctx

class EventDeleteView(View):
    def get(self, request, *args, **kwargs):
        if kwargs.get('pk') and News.objects.filter(pk=kwargs.get('pk')).exists():
            News.objects.filter(pk=kwargs.get('pk')).delete()
        return HttpResponse('OK')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(EventDeleteView, self).dispatch(request, *args, **kwargs)


class EventsListView(LeftMenuMixin, ListView):
    model = News
    context_object_name = 'news'
    template_name = 'communicate_list.html'
    sort_val = 'day'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(EventsListView, self).dispatch(request, *args, **kwargs)


    def get_queryset(self):
        qs = News.objects.order_by('-created')
        if self.request.GET.get('sort'):
            self.sort_val = self.request.GET.get('sort')
            self.request.session['sort'] = self.sort_val
        else:
            self.sort_val = self.request.session.get('sort', self.sort_val)
        if self.sort_val == 'day':
            day_ago = arrow.utcnow().replace(hours=-24).datetime
            return qs.filter(created__gte=day_ago)
        if self.sort_val == 'week':
            day_ago = arrow.utcnow().replace(days=-7).datetime
            return qs.filter(created__gte=day_ago)
        if self.sort_val == 'month':
            day_ago = arrow.utcnow().replace(days=-30).datetime
            return qs.filter(created__gte=day_ago)
        return qs

    def post(self, request, *args, **kwargs):
        if request.POST.get('new-news'):
            nn = request.POST.get('new-news')
            if u'http://' in nn:
                n,cr = News.objects.get_or_create(
                    link=nn
                )
                n.users.add(request.user)
                if not n.group:
                    n.group = NewsGroup.objects.get(name=u'News')
                n.save()
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(EventsListView, self).get_context_data(**kwargs)
        ctx['groups'] = NewsGroup.objects.all()
        ctx['sort_val'] = self.sort_val
        ctx['active'] = 'events'
        return ctx

class EventsGroupListView(EventsListView):
    def get_queryset(self):
        ng = NewsGroup.objects.get(pk=self.kwargs.get('pk'))
        qs = super(EventsGroupListView, self).get_queryset()
        return qs.filter(group__pk=ng.pk)