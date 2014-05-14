#coding: utf-8
# Create your views here.
from app.models import News, NewsGroup
from django.views.generic import ListView, View
from django.http import HttpResponse
import arrow

class EventDeleteView(View):
    def get(self, request, *args, **kwargs):
        if kwargs.get('pk') and News.objects.filter(pk=kwargs.get('pk')).exists():
            News.objects.filter(pk=kwargs.get('pk')).delete()
        return HttpResponse('OK')

class EventsListView(ListView):
    model = News
    context_object_name = 'news'
    template_name = 'communicate_list.html'

    def get_queryset(self):
        qs = News.objects.order_by('-created')
        sort_val = ''
        if self.request.GET.get('sort'):
            sort_val = self.request.GET.get('sort')
            self.request.session['sort'] = sort_val
        else:
            sort_val = self.request.session.get('sort', '')
        if sort_val == 'day':
            day_ago = arrow.utcnow().replace(hours=-24).datetime
            return qs.filter(created__gte=day_ago)
        if sort_val == 'week':
            day_ago = arrow.utcnow().replace(days=-7).datetime
            return qs.filter(created__gte=day_ago)
        if sort_val == 'month':
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
                n.group = NewsGroup.objects.get(name=u'News')
                n.save()
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(EventsListView, self).get_context_data(**kwargs)
        ctx['groups'] = NewsGroup.objects.all()
        return ctx