#coding: utf-8
# Create your views here.
from app.models import News, NewsGroup
from django.views.generic import ListView

class EventsListView(ListView):
    model = News
    context_object_name = 'news'
    template_name = 'communicate_list.html'

    def get_context_data(self, **kwargs):
        ctx = super(EventsListView, self).get_context_data(**kwargs)
        ctx['groups'] = NewsGroup.objects.all()
        return ctx