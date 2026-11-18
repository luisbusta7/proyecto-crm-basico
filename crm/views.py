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
from django.db.models import Count, Max
from django.http import HttpResponse
from django.views import View
from .forms import ClientForm, InteractionForm
from .models import Client, Interaction
from django.utils import timezone

import csv  
# importamos workbook de openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill





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
    
    
    def get_queryset(self):
        self.query = self.request.GET.get("q", "").strip()
        return super().get_queryset().search(self.query)
        
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.query
        return context


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
    
    
# --- Exportación de clientes ---


class ClientExportBaseView(LoginRequiredMixin, VisibleClientsMixin, View):
    """Prepara los datos de exportación. Las subclases deciden el formato."""

    headers = [
        "Nombre",
        "Apellidos",
        "Email",
        "Teléfono",
        "Empresa",
        "Comercial asignado",
        "Nº interacciones",
        "Última interacción",
        "Fecha de alta",
    ]

    def get_queryset(self):
        query = self.request.GET.get("q", "").strip()
        return (
            super()
            .get_queryset()
            .search(query)
            .annotate(
                interactions_count=Count("interactions"),
                last_interaction=Max("interactions__date"),
            )
        )

    def get_rows(self):
        for client in self.get_queryset():
            yield [
                client.first_name,
                client.last_name,
                client.email,
                client.phone,
                client.company.name if client.company else "",
                str(client.sales_rep) if client.sales_rep else "",
                client.interactions_count,
                self.to_local(client.last_interaction),
                self.to_local(client.created_at),
            ]

    @staticmethod
    def to_local(value):
        if value is None:
            return None
        return timezone.localtime(value).replace(tzinfo=None)

    def get_filename(self, extension):
        return f"clientes_{timezone.localdate():%Y-%m-%d}.{extension}"


class ClientExportCSVView(ClientExportBaseView):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = (
            f'attachment; filename="{self.get_filename("csv")}"'
        )
        response.write("\ufeff")

        writer = csv.writer(response, delimiter=";")
        writer.writerow(self.headers)
        for row in self.get_rows():
            writer.writerow([self.format_csv_value(value) for value in row])
        return response


    @staticmethod
    def format_csv_value(value):
        if value is None:
            return ""
        if hasattr(value, "strftime"):
            return value.strftime("%d/%m/%Y %H:%M")
        return value


class ClientExportExcelView(ClientExportBaseView):
    def get(self, request, *args, **kwargs):
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Clientes"

        sheet.append(self.headers)
        for row in self.get_rows():
            sheet.append(row)

        # Cabecera en negrita, blanco sobre gris oscuro
        for cell in sheet[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="212529")

        # Formato de fecha en las dos últimas columnas
        for row in sheet.iter_rows(min_row=2, min_col=8, max_col=9):
            for cell in row:
                cell.number_format = "DD/MM/YYYY HH:MM"

        # Ancho de cada columna según su contenido más largo
        for column in sheet.columns:
            longest = max(len(str(cell.value or "")) for cell in column)
            sheet.column_dimensions[column[0].column_letter].width = min(longest + 2, 50)

        sheet.freeze_panes = "A2"
        sheet.auto_filter.ref = sheet.dimensions

        response = HttpResponse(
            content_type=(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        )
        response["Content-Disposition"] = (
            f'attachment; filename="{self.get_filename("xlsx")}"'
        )
        workbook.save(response)
        return response
