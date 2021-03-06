#coding: utf-8
# Create your views here.
from app.models import GAProfile
from datetime import date
from django.contrib.auth.forms import PasswordChangeForm
from dateutil.relativedelta import relativedelta
from django.views.generic import ListView, View, TemplateView, DetailView, UpdateView, CreateView, FormView
from django.views.generic.base import ContextMixin
from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.shortcuts import redirect
import arrow, logging, hashlib
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sites.models import get_current_site
from reportlab.pdfgen import canvas

from app.models import *
from talk.models import *
from app.forms import *
from steps.models import Step
from django import forms
import json, os, hashlib
import httplib2

from datetime import datetime, timedelta

from apiclient.discovery import build
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from app.models import CredentialsModel, GAFunnelConfig
from django.conf import settings
from oauth2client import xsrfutil
from oauth2client.client import flow_from_clientsecrets
from oauth2client.django_orm import Storage
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail

# OAuth2.0 process
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), '..','absly', 'client_secrets.json')

FLOW = flow_from_clientsecrets(
    CLIENT_SECRETS,
  scope='https://www.googleapis.com/auth/analytics.readonly',
    redirect_uri='http://new.absly.com/oauth2callback/')

class SubscribeView(View):
    def post(self, request, *args, **kwargs):
        if request.POST.get('email'):
            send_mail(u'New subscriber', request.POST.get('email'), 'info@absly.com', ['lifanov@absly.com'])
        return HttpResponse('OK')

class LandingView(TemplateView):
    template_name = 'landing.html'

class RegisterView(TemplateView):
    template_name = 'registration/custom-register.html'
    form = None

    def post(self, request, *args, **kwargs):
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            new_user = User.objects.create(
                username=data['email'],
                email=data['email']
            )
            new_user.set_password(data['password'])
            new_user.is_active = True
            new_user.save()
            # send mail
            send_mail(u'Привет. Вот твой пароль для new.absly.com', u'Ваш логин: {}\nВаш пароль: {}'.format(data['email'], data['password']), u'lifanov@absly.com',
                      [data['email'],])

            # login
            user = authenticate(username=data['email'], password=data['password'])
            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                raise ValueError("User not found")
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(RegisterView, self).get_context_data(**kwargs)
        if not self.form:
            self.form = RegisterForm()
        ctx['form'] = self.form
        return ctx

class StepsSortView(View):
    def get(self, request, *args, **kwargs):
        request.session['steps_sort_customer'] = request.GET.get('customer')
        request.session['steps_sort_product'] = request.GET.get('product')
        request.session['steps_sort_fundrising'] = request.GET.get('fundrising')
        return HttpResponse("OK")

class CreateProjectView(TemplateView):
    template_name = 'project/create.html'
    formset = forms.models.modelformset_factory(Customer, max_num=5, extra=4, exclude=['project',])

    def post(self, request, *args, **kwargs):
        form = ProjectForm(request.POST)
        if form.is_valid():
            prj = form.save()
            prj.user=request.user
            prj.save()
            fs = self.formset(request.POST)
            if fs.is_valid():
                customers = fs.save()
                for customer in customers:
                    customer.project = prj
                    customer.save()
            prj.fill_data()
        return HttpResponseRedirect('/')

    def get_context_data(self, **kwargs):
        ctx = super(CreateProjectView, self).get_context_data(**kwargs)
        ctx['project_form'] = ProjectForm()
        ctx['project_customers_formset'] = self.formset(queryset=Customer.objects.none())
        return ctx

class StatisticsMixin(ContextMixin):
    stage = 'angel'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):

        if not Project.objects.filter(user=self.request.user).exists():
            return HttpResponseRedirect('/new/')
        return super(StatisticsMixin, self).dispatch(*args, **kwargs)

    def calc_certainly_level(self):
        ls = 0.0
        if CanvasBlock.objects.filter(name__in=[u'Value Proposition', u'Customer Segments'], elements__isnull=True):
            return ls
        for block in CanvasBlock.objects.all():
            if block.name in [u'Customer Segments', u'Value Proposition', u'Channels', u'Revenue Streams']:
                ls += 3.0*block.get_certainly_level(self.request.user)/22.0
            else:
                ls += 2.0*block.get_certainly_level(self.request.user)/22.0
        return round(ls)

    def get_valuation_score(self, valuation):
        if 0.5 <= valuation <= 0.65:
            self.stage = 'angel'
            return 3.0
        if 0.65 < valuation <= 0.8:
            self.stage = 'angel'
            return 2.0
        if 0.8 < valuation <= 1.0:
            self.stage = 'angel'
            return 1.0
        if 1.0 < valuation <= 2.0:
            self.stage = 'seed'
            return 3.0
        if 2.0 < valuation <= 3.0:
            self.stage = 'seed'
            return 2.0
        if 3.0 < valuation <= 4.0:
            self.stage = 'seed'
            return 1.0
        if 4.0 < valuation <= 6.0:
            self.stage = 'sa'
            return 3.0
        if 6.0 < valuation <= 8.0:
            self.stage = 'sa'
            return 2.0
        if 8.0 < valuation <= 10.0:
            self.stage = 'sa'
            return 1.0
        return 0.0

    def get_fr_certainly_level(self):
        l = self.calc_certainly_level()
        l_score = 0.0
        if 0 <= l <= 10.0 and self.stage == 'angel': return 0.0
        if 10.0 < l <= 20.0 and self.stage == 'angel': return 1.0
        if 20.0 < l <= 40.0 and self.stage == 'angel': return 2.0
        if l > 40.0 and self.stage == 'angel': return 3.0

        if l < 50.0 and self.stage == 'seed': return 0.0
        if 50.0 <= l <= 60.0 and self.stage == 'seed': return 1.0
        if 60.0 < l <= 70.0 and self.stage == 'seed': return 2.0
        if l > 70.0 and self.stage == 'seed': return 3.0

        if l < 70.0 and self.stage == 'sa': return 0.0
        if 70.0 <= l <= 80.0 and self.stage == 'sa': return 1.0
        if 80.0 < l <= 90.0 and self.stage == 'sa': return 2.0
        if l > 90.0 and self.stage == 'sa': return 3.0

        return l_score

    def get_market_score(self):
        if SummaryMarketBlock.objects.filter(user=self.request.user).exists():
            market_size = SummaryMarketBlock.objects.filter(user=self.request.user).all()[0].size
            if market_size < 100.0: return 0.0
            if 100.0 <= market_size <= 500.0: return 1.0
            if 500.0 < market_size <= 1000.0: return 2.0
            if market_size > 1000.0: return 3.0
        return 0.0

    def calc_funding_ready(self):
        fr = 0.0
        if SummaryValuationBlock.objects.filter(user=self.request.user).exists():
            valuation = SummaryValuationBlock.objects.filter(user = self.request.user).all()[0].size
            fr = self.get_valuation_score(valuation) + 2.0*self.get_fr_certainly_level() + self.get_market_score()
            fr = 100.0*fr/18.0

        return fr

    def get_context_data(self, **kwargs):
        ctx = super(StatisticsMixin, self).get_context_data(**kwargs)
        ga_funnel_config, created = GAFunnelConfig.objects.get_or_create(
            user=self.request.user
        )
        logdata = GALogData.objects.filter(user=self.request.user).order_by('-end_date')
        if ga_funnel_config.user_sum and logdata.count():
            logdata = logdata[0]
            ctx['money_sum'] = logdata.r3*ga_funnel_config.user_sum
            ctx['money_time'] = ga_funnel_config.date_range
        ctx['certainly_level'] = int(self.calc_certainly_level())
        ctx['funding_ready_level'] = int(self.calc_funding_ready())
        return ctx

class LeftMenuMixin(StatisticsMixin):
    def get_context_data(self, **kwargs):
        ctx = super(LeftMenuMixin, self).get_context_data(**kwargs)
        ctx['summary_groups'] = SummaryGroup.objects.all()
        return ctx

class UpdateTopStatisticsView(StatisticsMixin, View):
    def get(self, request, *args, **kwargs):
        ctx = {
            'certainly_level': int(self.calc_certainly_level())
        }
        return HttpResponse(json.dumps(ctx), content_type='application/json')


@login_required
def auth_return(request):
  if not xsrfutil.validate_token(settings.SECRET_KEY, request.REQUEST['state'],
                                 request.user):
    return  HttpResponseBadRequest()
  credential = FLOW.step2_exchange(request.REQUEST)
  storage = Storage(CredentialsModel, 'id', request.user, 'credential')
  storage.put(credential)
  return HttpResponseRedirect("/ga-config/")

class GAFunnelView(LeftMenuMixin, TemplateView):
    credentials = None
    template_name = 'ga-funnel.html'
    ga_funnel_config = None
    ga_profile = None
    service = None
    logdata = None

    def post(self, request, *args, **kwargs):
        self.logdata = GALogData.objects.filter(user=request.user).order_by('-end_date')[0]
        form = GALogDataForm(request.POST, instance=self.logdata)
        if form.is_valid():
            form.save()
        # if request.POST.get('activation_value'):
        #     self.logdata.a2 = request.POST.get('activation_value')
        # if request.POST.get('retention_value'):
        #     self.logdata.r1 = request.POST.get('retention_value')
        # if request.POST.get('referral_value'):
        #     self.logdata.r2 = request.POST.get('referral_value')
        # if request.POST.get('revenue_value'):
        #     self.logdata.r3 = request.POST.get('revenue_value')
        # self.logdata.save()
        return self.get(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if not self.ga_funnel_config:
            self.ga_funnel_config, created = GAFunnelConfig.objects.get_or_create(
                user=request.user
            )
            if not self.logdata:
                if not GALogData.objects.filter(user=request.user, end_date__gte=datetime.now()).exists():
                    oldlogdata = GALogData.objects.filter(user=request.user).order_by('-end_date')[0]
                    newlogdata = GALogData.objects.create(
                        user=request.user,
                        start_date=oldlogdata.end_date,
                        end_date=oldlogdata.end_date + relativedelta(months=self.ga_funnel_config.date_range)
                    )
                    self.logdata = newlogdata
                else:
                    self.logdata = GALogData.objects.filter(user=request.user, end_date__gte=datetime.now())[0]

        storage = Storage(CredentialsModel, 'id', self.request.user, 'credential')
        self.credential = storage.get()
        if self.credential is None or self.credential.invalid == True:
            return redirect(reverse('ga-config-view'))
        else:
            return super(GAFunnelView, self).get(request, *args, **kwargs)

    def get_ga_data(self, **kwargs):
        kwargs['ids'] = 'ga:{}'.format(self.ga_profile.profile_id)
        kwargs['start_date'] = self.logdata.get_start_str()
        kwargs['end_date'] = self.logdata.get_end_str()
        return self.service.data().ga().get(**kwargs).execute()

    def get_context_data(self, **kwargs):
        ctx = super(GAFunnelView, self).get_context_data(**kwargs)
        http = httplib2.Http()
        http = self.credential.authorize(http)
        self.service = build("analytics", "v3", http=http)

        self.ga_profile,created = GAProfile.objects.get_or_create(user=self.request.user)
        self.ga_funnel_config,created = GAFunnelConfig.objects.get_or_create(user=self.request.user)

        gaLogDataForm = GALogDataForm(instance=self.logdata)

        ga_users = self.get_ga_data(metrics='ga:users')
        if ga_users.get('rows'):
            ctx['ga_users'] = ga_users.get('rows')[0][0]
            self.logdata.a1 = int(ctx['ga_users'])
            self.logdata.save()

        # fcf = FunnelConfgiForm(instance=self.ga_funnel_config)
        # ctx['funnel_config_form'] = fcf


        if self.ga_funnel_config.activation_page:
            ctx['activation_value'] = self.get_ga_data(
                metrics='ga:users', max_results=1,
                filters='ga:pagePath=={}'.format(self.ga_funnel_config.activation_page)
            ).get('rows')[0][0]
        elif self.ga_funnel_config.activation_event_category:
            ff = u''
            if self.ga_funnel_config.activation_event_category:
                ff = u'ga:eventCategory=={}'.format(self.ga_funnel_config.activation_event_category)
            if self.ga_funnel_config.activation_event_action:
                ff += u';ga:eventAction=={}'.format(self.ga_funnel_config.activation_event_action)
            if self.ga_funnel_config.activation_event_label:
                ff += u';ga:eventLabel=={}'.format(self.ga_funnel_config.activation_event_label)
            ctx['activation_value'] = self.get_ga_data(metrics='ga:users', max_results=1, filters=ff).get('rows')[0][0]
        if 'activation_value' in ctx:
            self.logdata.a2 = ctx['activation_value']
            self.logdata.save()
            gaLogDataForm.fields['a2'].readonly = True

        if self.ga_funnel_config.retention_page:
            ctx['retention_value'] = self.get_ga_data(
                metrics='ga:users', max_results=1,
                filters='ga:pagePath=={}'.format(self.ga_funnel_config.retention_page)
            ).get('rows')[0][0]
        elif self.ga_funnel_config.retention_event_category:
            ff = u''
            if self.ga_funnel_config.retention_event_category:
                ff = u'ga:eventCategory=={}'.format(self.ga_funnel_config.retention_event_category)
            if self.ga_funnel_config.retention_event_action:
                ff += u';ga:eventAction=={}'.format(self.ga_funnel_config.retention_event_action)
            if self.ga_funnel_config.retention_event_label:
                ff += u';ga:eventLabel=={}'.format(self.ga_funnel_config.retention_event_label)
            ctx['retention_value'] = self.get_ga_data(metrics='ga:users', max_results=1, filters=ff).get('rows')[0][0]
        if 'retention_value' in ctx:
            self.logdata.r1 = ctx['retention_value']
            self.logdata.save()
            gaLogDataForm.fields['r1'].readonly = True

        if self.ga_funnel_config.referral_page:
            ctx['referral_value'] = self.get_ga_data(
                metrics='ga:users', max_results=1,
                filters='ga:pagePath=={}'.format(self.ga_funnel_config.referral_page)
            ).get('rows')[0][0]
        elif self.ga_funnel_config.referral_event_category:
            ff = u''
            if self.ga_funnel_config.referral_event_category:
                ff = u'ga:eventCategory=={}'.format(self.ga_funnel_config.referral_event_category)
            if self.ga_funnel_config.referral_event_action:
                ff += u';ga:eventAction=={}'.format(self.ga_funnel_config.referral_event_action)
            if self.ga_funnel_config.referral_event_label:
                ff += u';ga:eventLabel=={}'.format(self.ga_funnel_config.referral_event_label)
            ctx['referral_value'] = self.get_ga_data(metrics='ga:users', max_results=1, filters=ff).get('rows')[0][0]
        if 'referral_value' in ctx:
            self.logdata.r2 = ctx['referral_value']
            self.logdata.save()
            gaLogDataForm.fields['r2'].readonly = True

        if self.ga_funnel_config.revenue_page:
            ctx['revenue_value'] = self.get_ga_data(
                metrics='ga:users', max_results=1,
                filters='ga:pagePath=={}'.format(self.ga_funnel_config.referral_page)
            ).get('rows')[0][0]
        elif self.ga_funnel_config.revenue_event_category:
            ff = u''
            if self.ga_funnel_config.revenue_event_category:
                ff = u'ga:eventCategory=={}'.format(self.ga_funnel_config.revenue_event_category)
            if self.ga_funnel_config.revenue_event_action:
                ff += u';ga:eventAction=={}'.format(self.ga_funnel_config.revenue_event_action)
            if self.ga_funnel_config.revenue_event_label:
                ff += u';,ga:eventLabel=={}'.format(self.ga_funnel_config.revenue_event_label)
            ctx['revenue_value'] = self.get_ga_data(metrics='ga:users', max_results=1, filters=ff).get('rows')[0][0]
        if 'revenue_value' in ctx:
            self.logdata.r3 = ctx['revenue_value']
            self.logdata.save()
            gaLogDataForm.fields['r3'].readonly = True

        ctx['funnel_data_form'] = gaLogDataForm

        ll = GALogData.objects.filter(user=self.request.user).order_by('end_date')[:12]
        ctx['a1_list'] = json.dumps([ [i+1, n.a1] for i,n in enumerate(ll)])
        ctx['a2_list'] = json.dumps([ [i+1, n.a2] for i,n in enumerate(ll)])
        ctx['r1_list'] = json.dumps([ [i+1, n.r1] for i,n in enumerate(ll)])
        ctx['r2_list'] = json.dumps([ [i+1, n.r2] for i,n in enumerate(ll)])
        ctx['r3_list'] = json.dumps([ [i+1, n.r3] for i,n in enumerate(ll)])
        ctx['ticks'] = json.dumps([ [i+1, n.get_end_str()] for i,n in enumerate(ll)])
        return ctx

class GAFunnelConfigAjaxView(View):
    def post(self, request, *args, **kwargs):
        ga_funnel_config = GAFunnelConfig.objects.get(
            user=request.user
        )
        # date_range = request.POST.get('date_range')
        # if date_range:
        #     return HttpResponse("OK")
        fcf = FunnelConfgiForm(request.POST, instance=ga_funnel_config)
        fdf = FunnelDateForm(request.POST, instance=ga_funnel_config)
        if fdf.is_valid():
            fdf.save()
            logdata = GALogData.objects.filter(user=request.user).order_by('-end_date')[0]
            if not logdata.start_date:
                logdata.start_date = datetime.now()
            logdata.end_date = logdata.start_date + relativedelta(months=ga_funnel_config.date_range)
            logdata.save()

            # now = date.today()
            # end_date = now.strftime('%Y-%m-%d')
            # start_date = now + relativedelta(months=-ga_funnel_config.date_range)
            # start_date = start_date.strftime('%Y-%m-%d')
            # ga_funnel_config.date_range = ga_funnel_config.date_range
            # ga_funnel_config.start_date = start_date
            # ga_funnel_config.end_date = end_date
            # ga_funnel_config.save()
            return HttpResponse("OK")
        if fcf.is_valid():
            fcf.save()
            return HttpResponse("OK")
        return HttpResponse("{} [{}]".format(fdf.errors, fcf.errors))

class GAWeboptsView(View):

    def post(self, request, *args, **kwargs):
        account = request.POST.get('account')
        ga_profile,created = GAProfile.objects.get_or_create(
            user=request.user
        )
        if account:
            ga_profile.account_id = account
            ga_profile.save()
            storage = Storage(CredentialsModel, 'id', self.request.user, 'credential')
            self.credential = storage.get()
            if self.credential is None or self.credential.invalid == True:
                return HttpResponseForbidden
            else:
                http = httplib2.Http()
                http = self.credential.authorize(http)
                service = build("analytics", "v3", http=http)
                wps = service.management().webproperties().list(accountId=account).execute()
                webprops_config = []
                for wp in wps.get('items'):
                    webprops_config.append((wp.get('id'), wp.get('name')))
                data = {
                    'data': render_to_string('widgets/ga/account.html', {
                        'items': webprops_config,
                        'item_name': 'webprops',
                        'selected_item': ga_profile.webproperty_id
                    })
                }
                return HttpResponse(json.dumps(data), content_type='application/json')

class GAProfileView(View):

    def post(self, request, *args, **kwargs):
        webprops = request.POST.get('webprops')
        ga_profile,created = GAProfile.objects.get_or_create(
            user=request.user
        )
        if webprops:
            ga_profile.webproperty_id = webprops
            ga_profile.save()
            storage = Storage(CredentialsModel, 'id', self.request.user, 'credential')
            self.credential = storage.get()
            if self.credential is None or self.credential.invalid == True:
                return HttpResponseForbidden
            else:
                http = httplib2.Http()
                http = self.credential.authorize(http)
                service = build("analytics", "v3", http=http)
                profiles = service.management().profiles().list(
                    accountId=ga_profile.account_id,
                    webPropertyId=ga_profile.webproperty_id
                ).execute()
                webprops_config = []
                for wp in profiles.get('items'):
                    webprops_config.append((wp.get('id'), wp.get('name')))
                data = {
                    'data': render_to_string('widgets/ga/account.html', {
                        'items': webprops_config,
                        'item_name': 'profile',
                        'selected_item': ga_profile.webproperty_id
                    })
                }
                return HttpResponse(json.dumps(data), content_type='application/json')
        return HttpResponseForbidden()

class GAProfileCompletedView(View):

    def post(self, request, *args, **kwargs):
        profile = request.POST.get('profile')
        ga_profile,created = GAProfile.objects.get_or_create(
            user=request.user
        )
        if profile:
            ga_profile.profile_id = profile
            ga_profile.save()
            return HttpResponse("OK")
        return HttpResponseForbidden()

class GAConfigView(LeftMenuMixin, TemplateView):
    credentials = None
    template_name = 'ga.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(GAConfigView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(GAConfigView, self).get_context_data(**kwargs)
        ga_profile, created = GAProfile.objects.get_or_create(
            user=self.request.user
        )
        ga_funnel_config,created = GAFunnelConfig.objects.get_or_create(
            user=self.request.user
        )
        if not GALogData.objects.filter(user=self.request.user).exists():
            logdata = GALogData.objects.create(
                user=self.request.user,
                start_date = datetime.now(),
                end_date = datetime.now() + relativedelta(months=1)
            )
        else:
            logdata = GALogData.objects.filter(user=self.request.user).order_by('-end_date')[0]
        # if created or not ga_funnel_config.end_date or not ga_funnel_config.start_date:
        #     ga_funnel_config.end_date = date.today().strftime('%Y-%m-%d')
        #     ga_funnel_config.start_date = date.today() + relativedelta(months=-1)
        #     ga_funnel_config.start_date = ga_funnel_config.start_date.strftime('%Y-%m-%d')
        #     ga_funnel_config.save()
        storage = Storage(CredentialsModel, 'id', self.request.user, 'credential')
        self.credential = storage.get()
        if self.credential is None or self.credential.invalid == True:
            FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY, self.request.user)
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
            if ga_profile.account_id and logdata.start_date and logdata.end_date:
                ctx['account'] = ga_profile.account_id

                ga_pages = service.data().ga().get(
                    ids='ga:{}'.format(ga_profile.profile_id),
                    start_date=logdata.get_start_str(),
                    end_date=logdata.get_end_str(),
                    metrics='ga:users',
                    dimensions='ga:pagePath',
                    max_results=125
                ).execute()
                if ga_pages.get('rows'):
                    ctx['ga_pages'] = [p[0] for p in ga_pages.get('rows')]

                ga_events_categories = service.data().ga().get(
                    ids='ga:{}'.format(ga_profile.profile_id),
                    start_date=logdata.get_start_str(),
                    end_date=logdata.get_end_str(),
                    metrics='ga:users',
                    dimensions='ga:eventCategory',
                    max_results=25
                ).execute()
                if ga_events_categories.get('rows'):
                    ctx['ga_events_categories'] = [p[0] for p in ga_events_categories.get('rows')]

                ga_events_actions = service.data().ga().get(
                    ids='ga:{}'.format(ga_profile.profile_id),
                    start_date=logdata.get_start_str(),
                    end_date=logdata.get_end_str(),
                    metrics='ga:users',
                    dimensions='ga:eventAction',
                    max_results=25
                ).execute()
                if ga_events_actions.get('rows'):
                    ctx['ga_events_actions'] = [p[0] for p in ga_events_actions.get('rows')]

                ga_events_labels = service.data().ga().get(
                    ids='ga:{}'.format(ga_profile.profile_id),
                    start_date=logdata.get_start_str(),
                    end_date=logdata.get_end_str(),
                    metrics='ga:users',
                    dimensions='ga:eventLabel',
                    max_results=25
                ).execute()
                if ga_events_labels.get('rows'):
                    ctx['ga_events_labels'] = [p[0] for p in ga_events_labels.get('rows')]

                fcf = FunnelConfgiForm(instance=ga_funnel_config)
                if 'ga_pages' in ctx:
                    vars = [(c,c) for c in ctx['ga_pages']]
                    vars.insert(0, (u'', '-----'))
                    field = forms.ChoiceField(
                        widget=forms.Select, choices=vars
                    )
                    fcf.fields['activation_page'] = field
                    fcf.fields['retention_page'] = field
                    fcf.fields['referral_page'] = field
                    fcf.fields['revenue_page'] = field

                if 'ga_events_categories' in ctx:
                    choices = [(c,c) for c in ctx['ga_events_categories']]
                    choices.insert(0, (u'', '----'))
                    field = forms.ChoiceField(
                        widget=forms.Select, choices=choices
                    )
                    fcf.fields['activation_event_category'] = field
                    fcf.fields['retention_event_category'] = field
                    fcf.fields['referral_event_category'] = field
                    fcf.fields['revenue_event_category'] = field

                if 'ga_events_actions' in ctx:
                    choices = [(c,c) for c in ctx['ga_events_actions']]
                    choices.insert(0, (u'', '----'))
                    field = forms.ChoiceField(
                        widget=forms.Select, choices=choices
                    )
                    fcf.fields['activation_event_action'] = field
                    fcf.fields['retention_event_action'] = field
                    fcf.fields['referral_event_action'] = field
                    fcf.fields['revenue_event_action'] = field

                if 'ga_events_labels' in ctx:
                    choices = [(c,c) for c in ctx['ga_events_labels']]
                    choices.insert(0, (u'', '----'))
                    field = forms.ChoiceField(
                        widget=forms.Select, choices=choices
                    )
                    fcf.fields['activation_event_label'] = field
                    fcf.fields['retention_event_label'] = field
                    fcf.fields['referral_event_label'] = field
                    fcf.fields['revenue_event_label'] = field
                ctx['funnel_config_form'] = fcf
                ctx['funnel_date_form'] = FunnelDateForm(instance=ga_funnel_config)
                ctx['funnel_date_form'].fields['date_range'] = forms.ChoiceField(
                    widget=forms.Select, choices=[
                        (1, u'1 месяц'),
                        (2, u'2 месяца'),
                        (3, u'3 месяца'),
                        (4, u'4 месяца'),
                        (5, u'5 месяцев'),
                        (6, u'6 месяцев'),
                        (12, u'12 месяцев'),
                        (24, u'24 месяца')
                    ]
                )
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
        return self.render_to_json_response([form.errors, form.non_field_errors()], status=400)

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

class DashboardView(LeftMenuMixin, TemplateView):
    template_name = 'dashboard.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(DashboardView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(DashboardView, self).get_context_data(**kwargs)
        ctx['active'] = 'dashboard'
        ctx['news'] = News.objects.order_by('-created')
        ctx['steps'] = Step.objects.filter(removed=False, user=self.request.user, status=False).order_by('deadline')
        ctx['ga_logs'] = GALogData.objects.filter(user=self.request.user).order_by('end_date')
        if not self.request.session.get('twice'):
            ctx['show_help'] = True
            self.request.session['twice'] = True
        if ctx['ga_logs']:
            ctx['ga_a1_list'] = json.dumps([[i+1, v.a1] for i,v in enumerate(ctx['ga_logs'])])
            ctx['ga_a2_list'] = json.dumps([[i+1, v.a2] for i,v in enumerate(ctx['ga_logs'])])
            ctx['ga_r1_list'] = json.dumps([[i+1, v.r1] for i,v in enumerate(ctx['ga_logs'])])
            ctx['ga_r2_list'] = json.dumps([[i+1, v.r2] for i,v in enumerate(ctx['ga_logs'])])
            ctx['ga_r3_list'] = json.dumps([[i+1, v.r3] for i,v in enumerate(ctx['ga_logs'])])
            ctx['ga_dates'] = json.dumps([[i+1, v.end_date.strftime('%d.%m.%Y')] for i,v in enumerate(ctx['ga_logs'])])
        return ctx

class CanvasLogFormView(View):
    def get(self, request, *args, **kwargs):
        element = CanvasBlockItem.objects.get(pk=request.GET.get('element'), user=request.user)
        new_value = int(request.GET.get('new'))
        old_value = int(element.level)
        form = CanvasLogForm(initial={
            'element': element,
            'old_value': '{}'.format(old_value),
            'new_value': '{}'.format(new_value)
        })
        form.fields['old_value'].widget = forms.HiddenInput()
        form.fields['new_value'].widget = forms.HiddenInput()
        form.fields['element'].widget = forms.HiddenInput()
        csrf_token = request.COOKIES['csrftoken']
        d = {
            'data': render_to_string('bm-canvas/log.html', {
                'prev_status': ITEM_LEVEL_CHOICE[old_value][1],
                'next_status': ITEM_LEVEL_CHOICE[new_value][1],
                'log_form': form,
                'csrf_token_value': csrf_token
            })
        }
        return HttpResponse(json.dumps(d), content_type='application/json')

    def post(self,request, *args, **kwargs):
        form = CanvasLogForm(request.POST)
        if form.is_valid():
            log = form.save()
            log.element.level = log.new_value
            log.element.save()
            return HttpResponse(json.dumps({
                'pk': log.element.pk,
                'data': render_to_string('bm-canvas/element.html', {'it': log.element})
            }), content_type='application/json')
        else:
            raise ValueError(form.errors)

class CanvasElementGetFormView(View):
    def get(self, request, *args, **kwargs):
        if request.GET.get('block'):
            block = CanvasBlock.objects.get(pk=request.GET.get('block'))
            if block:
                form = CanvasElementForm(initial={
                    'block':block
                })
                form.fields['block'].widget = forms.HiddenInput()
                form.add_params(block)
                form.fields['segment'].queryset = CanvasBlockItem.objects.filter(block__name=u'Customer Segments', user=request.user)
                csrf_token = request.COOKIES['csrftoken']
                data = {
                    'data': render_to_string('bm-canvas/form.html', {'form': form, 'csrf_token_value': csrf_token,
                                                                     'block': block})
                }
                return HttpResponse(json.dumps(data), content_type='application/json')
        if request.GET.get('element'):
            el = CanvasBlockItem.objects.get(pk=request.GET.get('element'), user=request.user)
            if el:
                form = CanvasElementForm(instance=el)
                form.fields['block'].widget = forms.HiddenInput()
                form.add_params(el.block, el)
                form.fields['segment'].queryset = CanvasBlockItem.objects.filter(block__name=u'Customer Segments', user=request.user)
                csrf_token = request.COOKIES['csrftoken']
                data = {
                    'data': render_to_string('bm-canvas/form.html', {'form': form, 'csrf_token_value': csrf_token,
                                                                     'block': el.block})
                }
                return HttpResponse(json.dumps(data), content_type='application/json')
        return HttpResponseForbidden()

    def post(self, request, *args, **kwargs):
        if request.POST.get('element'):
            if request.POST.get('delete'):
                el = CanvasBlockItem.objects.get(pk=request.POST.get('element'), user=request.user)
                el_pk=el.pk
                el.delete()
                return HttpResponse(json.dumps({
                    'deleted': el_pk
                }), content_type='application/json')
            form = CanvasElementForm(request.POST, instance=CanvasBlockItem.objects.get(pk=request.POST.get('element')))
        else:
            form = CanvasElementForm(request.POST)
        if form.is_valid():
            el = form.save()
            el.user = request.user
            el.save()
            if request.POST.get('param_0'):
                p = request.POST['param_0']
                v = CanvasBlockItemParameterValue.objects.get(pk=p)
                v.elements.add(el)
            if request.POST.get('param_1'):
                p = request.POST['param_1']
                v = CanvasBlockItemParameterValue.objects.get(pk=p)
                v.elements.add(el)
            if request.POST.get('param_2'):
                p = request.POST['param_2']
                v = CanvasBlockItemParameterValue.objects.get(pk=p)
                v.elements.add(el)
            data = {
                'block': el.block.pk,
                'data': render_to_string('bm-canvas/element.html', {'it': el})
            }
            if request.POST.get('element'): data['pk'] = form.instance.pk
            return HttpResponse(json.dumps(data), content_type='application/json')
        return HttpResponseForbidden()

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
        ctx['cr'] = CanvasBlock.objects.get(slug='customer-relationship')
        ctx['cos'] = CanvasBlock.objects.get(slug='cost-structure')
        ctx['rs'] = CanvasBlock.objects.get(slug='revenue-streams')
        ctx['ch'] = CanvasBlock.objects.get(slug='channels')
        ctx['kr'] = CanvasBlock.objects.get(slug='key-resources')
        ctx['ka'] = CanvasBlock.objects.get(slug='key-activities')
        ctx['kp'] = CanvasBlock.objects.get(slug='key-partners')
        return ctx

class ExecutiveSummaryView(LeftMenuMixin, ListView):
    template_name = 'summary_list.html'
    model = SummaryGroup
    context_object_name = 'summary_groups'

    def get_queryset(self):
        return self.request.user.summary_items.filter(parent__isnull=True).all()

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ExecutiveSummaryView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(ExecutiveSummaryView, self).get_context_data(**kwargs)
        ctx['active'] = 'summary'
        s = get_current_site(self.request)
        m = hashlib.md5()
        m.update(self.request.user.email)
        ctx['snapshot_form'] = SnapshotForm()
        return ctx

class ExecutiveSummaryItemView(LeftMenuMixin, DetailView):
    template_name = 'summary.html'
    model = SummaryItem
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

class SummaryBlockView(CreateView):
    template_name = 'summary/forms/edit.html'
    success_url = '/summary/'

    def form_valid(self, form):
        block = form.save()
        block.user = self.request.user
        block.save()
        return self.get(self.request)

    def get_title(self):
        return u'Add block'

    def form_invalid(self, form):
        return HttpResponse(json.dumps(form.errors), content_type='application/json')

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial={
            'item': SummaryItem.objects.get(pk=self.request.GET.get('id'))
        })
        csrf_token = request.COOKIES['csrftoken']
        data = render_to_string(self.template_name, {'form': form, 'backurl': request.get_full_path(), 'csrf_token_value': csrf_token})
        return HttpResponse(json.dumps({'data': data, 'title': self.get_title()}), content_type='application/json')

class SummaryValuationBlockView(SummaryBlockView):
    model = SummaryValuationBlock
    form_class = SummaryValuationBlockForm

    def get_title(self):
        return u'Add valuation block'

class SummaryMarketSizeBlockView(SummaryBlockView):
    model = SummaryMarketBlock
    form_class = SummaryMarketSizeBlockForm

    def get_title(self):
        return u'Add market size block'

class SummaryInvestmentRequestBlockView(SummaryBlockView):
    model = SummaryInvestmentRequestBlock
    form_class = SummaryInvestmentRequestBlockForm

    def get_title(self):
        return u'Add investment request block'

class SummaryTextBlockView(SummaryBlockView):
    model = SummaryTextBlock
    form_class = SummaryTextBlockForm

    def get_title(self):
        return u'Add text block'

class SummaryImageBlockView(SummaryBlockView):
    model = SummaryImageBlock
    form_class = SummaryImageBlockForm

    def get_title(self):
        return u'Add image block'

class SummaryLinkBlockView(SummaryBlockView):
    model = SummaryLinkBlock
    form_class = SummaryLinkBlockForm

    def get_title(self):
        return u'Add link block'

class SummaryLinkedInBlockView(SummaryBlockView):
    model = SummaryLinkedInBlock
    form_class = SummaryLinkedInBlockForm

    def get_title(self):
        return u'Add LinkedIn block'

class SummaryAngelListBlockView(SummaryBlockView):
    model = SummaryAngelListBlock
    form_class = SummaryAngelListBlockForm

    def get_title(self):
        return u'Add AngelList block'

class SummaryCrunchBaseBlockView(SummaryBlockView):
    model = SummaryCrunchBaseBlock
    form_class = SummaryCrunchBaseBlockForm

    def get_title(self):
        return u'Add CrunchBase block'

class SummaryDeleteBlock(View):

    def get(self, request, *args, **kwargs):
        block = request.user.summary_blocks.get(pk=self.kwargs.get('pk'))
        block.delete()
        return HttpResponse('OK')

class SummaryUpdateBlockView(UpdateView):
    template_name = 'summary/forms/edit.html'
    model = SummaryBlock
    success_url = '/summary/'

    def get(self, request, *args, **kwargs):
        block = self.get_object()
        form = self.get_form_class()(instance=block)
        csrf_token = request.COOKIES['csrftoken']
        data = render_to_string(self.template_name, {'form': form, 'backurl': request.path, 'csrf_token_value': csrf_token})
        return HttpResponse(json.dumps({'data': data, 'title': self.get_title()}), content_type='application/json')


    def get_form_class(self):
        block = self.get_object()
        if block.__class__.__name__ == 'SummaryTextBlock':
            return SummaryTextBlockForm
        if block.__class__.__name__ == 'SummaryImageBlock':
            return SummaryImageBlockForm
        if block.__class__.__name__ == 'SummaryLinkBlock':
            return SummaryLinkBlockForm
        if block.__class__.__name__ == 'SummaryCrunchBaseBlock':
            return SummaryCrunchBaseBlockForm
        if block.__class__.__name__ == 'SummaryAngelListBlock':
            return SummaryAngelListBlockForm
        if block.__class__.__name__ == 'SummaryLinkedInBlock':
            return SummaryLinkedInBlockForm
        if block.__class__.__name__ == 'SummaryMarketBlock':
            return SummaryMarketSizeBlockForm
        if block.__class__.__name__ == 'SummaryValuationBlock':
            return SummaryValuationBlockForm
        if block.__class__.__name__ == 'SummaryInvestmentRequestBlock':
            return SummaryInvestmentRequestBlockForm
        return NotImplementedError(block.__class__.__name__)

    def get_title(self):
        block = self.get_object()
        if block.__class__.__name__ == 'SummaryTextBlock':
            return u'Edit text block'
        if block.__class__.__name__ == 'SummaryImageBlock':
            return u'Edit image block'
        if block.__class__.__name__ == 'SummaryLinkBlock':
            return u'Edit link block'
        if block.__class__.__name__ == 'SummaryCrunchBaseBlock':
            return u'Edit CrunchBase block'
        if block.__class__.__name__ == 'SummaryAngelListBlock':
            return u'Edit AngelList block'
        if block.__class__.__name__ == 'SummaryLinkedInBlock':
            return u'Edit LinkedIn block'
        if block.__class__.__name__ == 'SummaryValuationBlock':
            return u'Edit Valuation block'
        if block.__class__.__name__ == 'SummaryMarketBlock':
            return u'Edit Market Size block'
        if block.__class__.__name__ == 'SummaryInvestmentRequestBlock':
            return u'Edit Investment Request block'
        return NotImplementedError(block.__class__.__name__)

class SummaryPubView(TemplateView):
    template_name = 'summary/public.html'

    def get_context_data(self, **kwargs):
        ctx = super(SummaryPubView, self).get_context_data(**kwargs)
        ss = Snapshot.objects.get(hash=self.kwargs.get('hash'))
        ctx['json'] = json.loads(ss.data)
        ctx['project_name'] = ss.project_name
        return ctx


class PersonalDataView(LeftMenuMixin, FormView):
    template_name = 'registration/personal-data.html'
    form_class = PasswordChangeForm
    success_url = '/personal/'
    saved = False

    def form_valid(self, form):
        self.request.user.set_password(form.cleaned_data['new_password1'])
        self.request.user.save()
        self.saved = True
        return self.get(self.request)

    def get_context_data(self, **kwargs):
        ctx = super(PersonalDataView, self).get_context_data(**kwargs)
        ctx['saved'] = self.saved
        return ctx

    def get_form_kwargs(self, **kwargs):
        kw = super(PersonalDataView, self).get_form_kwargs(**kwargs)
        kw['user'] = self.request.user
        return kw

class SnapshotsListView(LeftMenuMixin, ListView):
    template_name = 'summary/snapshot_list.html'
    context_object_name = 'snapshots'

    def get_context_data(self, **kwargs):
        ctx = super(SnapshotsListView, self).get_context_data(**kwargs)
        ctx['active'] = 'summary'
        return ctx

    def get_queryset(self):
        return Snapshot.objects.filter(user=self.request.user).order_by('-created')

class TextPageView(DetailView):
    template_name = 'page.html'
    model = TextPage
    context_object_name = 'page'

class SnapshotView(View):
    def post(self, request, *args, **kwargs):
        if request.POST:
            form = SnapshotForm(request.POST)
            if form.is_valid():
                snapshot = form.save()
                snapshot.user = request.user
                m = hashlib.md5()
                m.update('{}{}'.format(request.user.email, snapshot.created))
                snapshot.hash = m.hexdigest()
                snapshot.project_name = Project.objects.get(user=request.user).name
                snapshot.save()
                snapshot.generate_json(request.user)
                return HttpResponse(json.dumps({
                    'link': 'http://new.absly.com/summary/public/{}/'.format(snapshot.hash)
                }), content_type='application/json')
            else:
                return HttpResponse(u"{}".format(form.errors), status=500)
        return HttpResponse("OK")