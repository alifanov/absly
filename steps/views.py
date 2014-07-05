from django.views.generic import TemplateView, View
from app.views import LeftMenuMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, HttpResponseForbidden
import json
from django.template.loader import render_to_string
from steps.models import *
from steps.forms import *

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

        ctx['customer_steps'] = self.request.user.steps.filter(type='C').order_by('deadline')
        ctx['product_steps'] = self.request.user.steps.filter(type='P').order_by('deadline')
        ctx['fundrising_steps'] = self.request.user.steps.filter(type='F').order_by('deadline')

        ctx['active'] = 'steps'
        return ctx

class StepAddView(View):
    def get(self, request, *args, **kwargs):
        form = StepForm()
        csrf_token = request.COOKIES['csrftoken']
        data = {
            'data': render_to_string('step-form.html', {'step_form': form, 'csrf_token_value': csrf_token})
        }
        return HttpResponse(json.dumps(data), content_type='application/json')

    def post(self, request, *args, **kwargs):
        form = StepForm(request.POST, initial={
            'user': request.user
        })
        if form.is_valid():
            form.save()
            return HttpResponse('OK')
        else:
            return HttpResponseForbidden()

class RecomendationView(View):
    def get(self, request, *args, **kwargs):
        r = request.GET.get('r')
        if r:
            r = request.user.recomendations.filter(pk=r)[0]
            csrf_token = request.COOKIES['csrftoken']
            data = {
                'data': render_to_string('recomendation.html', {'r': r, 'csrf_token_value': csrf_token})
            }
            return HttpResponse(json.dumps(data), content_type='application/json')

    def post(self, request, *args, **kwargs):
        r = request.GET.get('r')
        if r:
            r = request.user.recomendations.filter(pk=r)[0]
            step = r.create_step(request.user)
            r.users.remove(request.user)
            data = {'data': render_to_string('step-item.html', {'step': step})}
            return HttpResponse(json.dumps(data), content_type='application/json')