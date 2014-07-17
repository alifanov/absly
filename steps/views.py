from django.views.generic import TemplateView, View
from app.views import LeftMenuMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, HttpResponseForbidden
import json
from django.template.loader import render_to_string
from steps.models import *
from app.models import CanvasBlock
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

        ctx['customer_steps'] = self.request.user.steps.filter(type='C', status=False).order_by('deadline')
        ctx['product_steps'] = self.request.user.steps.filter(type='P', status=False).order_by('deadline')
        ctx['fundrising_steps'] = self.request.user.steps.filter(type='F', status=False).order_by('deadline')

        ctx['customer_done'] = self.request.user.steps.filter(type='C', status=True).order_by('deadline')
        ctx['product_done'] = self.request.user.steps.filter(type='P', status=True).order_by('deadline')
        ctx['fundrising_done'] = self.request.user.steps.filter(type='F', status=True).order_by('deadline')

        ctx['active'] = 'steps'
        return ctx

class StepDoneView(View):
    def get(self, request, *args, **kwargs):
        step = Step.objects.get(user=request.user, pk=self.kwargs.get('pk'))
        step.status = True
        step.save()
        return HttpResponse('OK')

class StepDelView(View):
    def get(self, request, *args, **kwargs):
        step = Step.objects.get(user=request.user, pk=self.kwargs.get('pk'))
        step.delete()
        return HttpResponse('OK')

class StepAddView(View):
    def get(self, request, *args, **kwargs):
        form = StepForm()
        csrf_token = request.COOKIES['csrftoken']
        blocks = []
        for b in CanvasBlock.objects.all():
            blocks.append(
                (b.name, b.elements.filter(user=request.user))
            )
        data = {
            'data': render_to_string('step-form.html', {'step_form': form, 'csrf_token_value': csrf_token, 'blocks': blocks})
        }
        return HttpResponse(json.dumps(data), content_type='application/json')

    def post(self, request, *args, **kwargs):
        form = StepForm(request.POST)
        if form.is_valid():
            step = form.save()
            step.user=request.user
            step.save()
            return HttpResponse('OK')
        else:
            return HttpResponseForbidden(u'{}'.format(form.errors))

class StepEditView(View):
    def get(self, request, *args, **kwargs):
        step = Step.objects.get(pk=self.kwargs.get('pk'))
        form = StepForm(instance=step)
        csrf_token = request.COOKIES['csrftoken']
        data = {
            'data': render_to_string('step-edit-form.html', {'step_form': form, 'csrf_token_value': csrf_token, 'step': step})
        }
        return HttpResponse(json.dumps(data), content_type='application/json')

    def post(self, request, *args, **kwargs):
        step = Step.objects.get(pk=self.kwargs.get('pk'))
        form = StepForm(request.POST, instance=step)
        if form.is_valid():
            step = form.save()
            return HttpResponse('OK')
        else:
            return HttpResponseForbidden(u'{}'.format(form.errors))

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