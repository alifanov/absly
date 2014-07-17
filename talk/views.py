from django.views.generic import TemplateView
from app.views import StatisticsMixin
class InvestorsRequestsView(StatisticsMixin, TemplateView):
    template_name = 'investors-requests.html'