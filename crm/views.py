from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from .forms import ClientForm, InteractionForm
from .models import Client, Interaction

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
    
    
class InteractionCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Interaction
    form_class = InteractionForm
    success_message = "Interacción creada correctamente."

    @cached_property
    def client_obj(self):
        return get_object_or_404(Client, pk=self.kwargs['client_pk'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = self.client_obj
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.client = self.client_obj
        return super().form_valid(form)
    
class InteractionUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Interaction
    form_class = InteractionForm
    success_message = "Interacción actualizada correctamente."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client_obj'] = self.object.client
        return context
    
class InteractionDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Interaction
    success_message = "Interacción eliminada correctamente."

    def get_success_url(self):
        return self.object.client.get_absolute_url()