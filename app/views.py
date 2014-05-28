#coding: utf-8
# Create your views here.
from app.models import News, NewsGroup
from django.views.generic import ListView, View, TemplateView, DetailView, UpdateView
from django.http import HttpResponse
import arrow
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required

from app.models import SummaryGroup, SummaryItem

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
        if self.request.is_ajax():
            return self.render_to_json_response(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
                }
            return self.render_to_json_response(data)
        else:
            return response

class LeftMenuMixin(object):
    def get_context_data(self, **kwargs):
        ctx = super(LeftMenuMixin, self).get_context_data(**kwargs)
        ctx['summary_groups'] = SummaryGroup.objects.order_by('order')
        return ctx

class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(DashboardView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(DashboardView, self).get_context_data(**kwargs)
        ctx['active'] = 'canvas'
        return ctx


class CanvasView(TemplateView):
    template_name = 'canvas.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(CanvasView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(CanvasView, self).get_context_data(**kwargs)
        ctx['active'] = 'canvas'
        return ctx

class ExecutiveSummaryView(LeftMenuMixin, TemplateView):
    template_name = 'summary.html'

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
    model = SummaryItem
    fields = ['text',]

class MetricsView(TemplateView):
    template_name = 'metrics.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(MetricsView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(MetricsView, self).get_context_data(**kwargs)
        ctx['active'] = 'metrics'
        return ctx

class StepsView(TemplateView):
    template_name = 'steps.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(StepsView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(StepsView, self).get_context_data(**kwargs)
        ctx['active'] = 'steps'
        return ctx

class StrategyView(TemplateView):
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


class EventsListView(ListView):
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