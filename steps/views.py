from django.views.generic import TemplateView
from app.views import LeftMenuMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from steps.models import *

class StepsView(LeftMenuMixin, TemplateView):
    template_name = 'steps.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(StepsView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(StepsView, self).get_context_data(**kwargs)
        ctx['customer_recomendations'] = self.request.user.recomendations.filter(type='C').order_by('-created')
        ctx['product_recomendations'] = self.request.user.recomendations.filter(type='P').order_by('-created')
        ctx['fundrising_recomendations'] = self.request.user.recomendations.filter(type='F').order_by('-created')
        ctx['active'] = 'steps'
        return ctx

