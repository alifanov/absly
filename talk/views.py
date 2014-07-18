from django.views.generic import TemplateView, ListView
from app.views import StatisticsMixin
from talk.models import *

class InvestorsRequestsView(StatisticsMixin, TemplateView):
    template_name = 'investors-requests.html'

    def get_context_data(self, **kwargs):
        ctx = super(InvestorsRequestsView, self).get_context_data(**kwargs)
        ctx['active'] = 'events'
        return ctx

class SystemView(StatisticsMixin, ListView):
    model = SystemNotification
    queryset = SystemNotification.objects.order_by('-created')
    template_name = 'system/list.html'
    context_object_name = 'ss'