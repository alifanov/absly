from django.views.generic import TemplateView, ListView, DetailView, FormView
from app.views import LeftMenuMixin
from django.http import Http404
from talk.models import *
from talk.forms import *

class PostsView(LeftMenuMixin, ListView):
    template_name = 'posts/list.html'
    context_object_name = 'ss'

    def get_queryset(self):
        return Post.objects.order_by('-created')

class InvestorsRequestsView(LeftMenuMixin, TemplateView):
    template_name = 'investors-requests.html'

    def get_context_data(self, **kwargs):
        ctx = super(InvestorsRequestsView, self).get_context_data(**kwargs)
        ctx['active'] = 'events'
        return ctx

class NewsView(LeftMenuMixin, ListView):
    model = News
    template_name = 'news/list.html'
    context_object_name = 'news'

    def get_context_data(self, **kwargs):
        ctx = super(NewsView, self).get_context_data(**kwargs)
        ctx['active'] = 'events'
        return ctx

    def get_queryset(self):
        return self.request.user.abslylikenews.filter(is_public=True).order_by('-created')

class SystemView(LeftMenuMixin, ListView):
    model = SystemNotification
    queryset = SystemNotification.objects.filter(is_public=True).order_by('-created')
    template_name = 'system/list.html'
    context_object_name = 'ss'

    def get_context_data(self, **kwargs):
        ctx = super(SystemView, self).get_context_data(**kwargs)
        ctx['active'] = 'events'
        return ctx

class SystemDetailView(LeftMenuMixin, DetailView, FormView):
    model = SystemNotification
    template_name = 'system/item.html'
    context_object_name = 's'
    form_class = SystemCommentForm

    def get_object(self, queryset=None):
        try:
            return self.model.objects.filter(is_public=True).get(pk=self.kwargs.get('pk'))
        except:
            raise Http404

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