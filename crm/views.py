from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'crm/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['my_clients_count'] = self.request.user.clients.count()
        return context