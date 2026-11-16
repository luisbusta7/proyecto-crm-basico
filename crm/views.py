from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from .forms import ClientForm
from .models import Client

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'crm/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['my_clients_count'] = self.request.user.clients.count()
        return context
    
# CRUD de clientes

class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    paginate_by = 10
    template_name = 'crm/client_list.html'
    
    def get_queryset(self):
        return Client.objects.select_related('company', 'sales_rep')
    

class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['interactions'] = self.object.interactions.select_related('user')
        return context
    

class ClientCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Client
    form_class = ClientForm
    success_message = "Cliente «%(first_name)s %(last_name)s» creado correctamente."

    def get_initial(self):
        return {"sales_rep": self.request.user}
    

class ClientUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Client
    form_class = ClientForm
    success_message = "Cliente «%(first_name)s %(last_name)s» actualizado."
    

class ClientDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Client
    success_url = reverse_lazy("crm:client_list")
    success_message = "Cliente eliminado."
