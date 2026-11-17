from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.functional import cached_property
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from .forms import ClientForm, InteractionForm
from .models import Client, Interaction


# --- Mixins reutilizables ---


class ManagerRequiredMixin(UserPassesTestMixin):
    """Solo deja pasar a responsables y superusuarios. El resto recibe un 403."""

    def test_func(self):
        return self.request.user.can_see_all


class VisibleClientsMixin:
    """Limita los clientes a los que el usuario puede ver."""

    def get_queryset(self):
        return Client.objects.visible_to(self.request.user).select_related(
            "company", "sales_rep"
        )


class ClientFormMixin:
    """Usa ClientForm y le pasa el usuario conectado."""

    form_class = ClientForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


# --- Inicio ---


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "crm/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["my_clients_count"] = user.clients.count()
        if user.can_see_all:
            context["total_clients_count"] = Client.objects.count()
        return context


# --- CRUD de clientes ---


class ClientListView(LoginRequiredMixin, VisibleClientsMixin, ListView):
    model = Client
    paginate_by = 10


class ClientDetailView(LoginRequiredMixin, VisibleClientsMixin, DetailView):
    model = Client

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["interactions"] = self.object.interactions.select_related("user")
        return context


class ClientCreateView(
    LoginRequiredMixin, ClientFormMixin, SuccessMessageMixin, CreateView
):
    model = Client
    success_message = "Cliente «%(first_name)s %(last_name)s» creado correctamente."

    def get_initial(self):
        return {"sales_rep": self.request.user}

    def form_valid(self, form):
        if "sales_rep" not in form.fields:
            form.instance.sales_rep = self.request.user
        return super().form_valid(form)


class ClientUpdateView(
    LoginRequiredMixin,
    VisibleClientsMixin,
    ClientFormMixin,
    SuccessMessageMixin,
    UpdateView,
):
    model = Client
    success_message = "Cliente «%(first_name)s %(last_name)s» actualizado."


class ClientDeleteView(
    LoginRequiredMixin, ManagerRequiredMixin, SuccessMessageMixin, DeleteView
):
    model = Client
    success_url = reverse_lazy("crm:client_list")
    success_message = "Cliente eliminado."


# --- CRUD de interacciones ---


class InteractionCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Interaction
    form_class = InteractionForm
    success_message = "Interacción registrada."

    @cached_property
    def client_obj(self):
        visible_clients = Client.objects.visible_to(self.request.user)
        return get_object_or_404(visible_clients, pk=self.kwargs["client_pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["client_obj"] = self.client_obj
        return context

    def form_valid(self, form):
        form.instance.client = self.client_obj
        form.instance.user = self.request.user
        return super().form_valid(form)


class VisibleInteractionsMixin:
    """Limita las interacciones a las de clientes que el usuario puede ver."""

    def get_queryset(self):
        return Interaction.objects.visible_to(self.request.user).select_related(
            "client"
        )


class InteractionUpdateView(
    LoginRequiredMixin, VisibleInteractionsMixin, SuccessMessageMixin, UpdateView
):
    model = Interaction
    form_class = InteractionForm
    success_message = "Interacción actualizada."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["client_obj"] = self.object.client
        return context


class InteractionDeleteView(
    LoginRequiredMixin, VisibleInteractionsMixin, SuccessMessageMixin, DeleteView
):
    model = Interaction
    success_message = "Interacción eliminada."

    def get_success_url(self):
        return self.object.get_absolute_url()