from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Client, Company, Interaction, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("CRM", {'fields': ('is_manager',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("CRM", {'fields': ('is_manager',)}),
    )
    list_display = UserAdmin.list_display + ('is_manager',)
    list_filter = UserAdmin.list_filter + ('is_manager',)



class InteractionInline(admin.TabularInline):
    model = Interaction
    extra = 0
    fields = ("date", "kind", "summary", "user")


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "website", "created_at")
    search_fields = ("name",)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("__str__", "email", "company", "sales_rep", "created_at")
    list_filter = ("sales_rep", "company")
    search_fields = ("first_name", "last_name", "email", "company__name")
    inlines = [InteractionInline]

@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ("client", "kind", "summary", "user", "date")
    list_filter = ("kind", "user")
    search_fields = ("summary", "client__first_name", "client__last_name")