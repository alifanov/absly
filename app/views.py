#coding: utf-8
# Create your views here.
from app.models import News, NewsGroup
from django.views.generic import ListView, View, TemplateView
from django.http import HttpResponse
import arrow
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required

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
        ctx['active'] = 'communicate'
        return ctx