from django.views.generic import TemplateView, ListView, DetailView, FormView
from app.views import StatisticsMixin
from talk.models import *
from talk.forms import *

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

    def get_context_data(self, **kwargs):
        ctx = super(SystemView, self).get_context_data(**kwargs)
        ctx['active'] = 'events'
        return ctx

class SystemDetailView(StatisticsMixin, DetailView, FormView):
    model = SystemNotification
    template_name = 'system/item.html'
    context_object_name = 's'
    form_class = SystemCommentForm

    def form_valid(self, form):
        comment = form.save()
        comment.user=self.request.user
        comment.notify = self.get_object()
        comment.save()
        return self.get(self.request)

    def get_context_data(self, **kwargs):
        ctx = super(SystemDetailView, self).get_context_data(**kwargs)
        ctx['form'] = self.form_class()
        ctx['active'] = 'events'
        return ctx