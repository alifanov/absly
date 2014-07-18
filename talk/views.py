from django.views.generic import TemplateView
from app.views import StatisticsMixin
class InvestorsRequestsView(StatisticsMixin, TemplateView):
    template_name = 'investors-requests.html'

    def get_context_data(self, **kwargs):
        ctx = super(InvestorsRequestsView, self).get_context_data(**kwargs)
        ctx['active'] = 'events'
        return ctx