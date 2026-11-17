from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.urls import reverse

class User(AbstractUser):
    is_manager = models.BooleanField("responsable comercial", default=False, help_text="Puede ver y gestionar los clientes de todos los comerciales")

    @property
    def can_see_all(self):
        return self.is_manager or self.is_superuser
    

class Company(models.Model):
    name = models.CharField("nombre", max_length=150, unique=True )
    website = models.URLField("sitio web", blank=True, null=True)
    phone = models.CharField("teléfono", max_length=20, blank=True, null=True)
    created_at = models.DateTimeField("fecha de creación", default=timezone.now)
    
    class Meta:
        verbose_name = 'empresa'
        verbose_name_plural = 'empresas'
        ordering = ['name']
        
    def __str__(self):
        return self.name



class ClientQuerySet(models.QuerySet):
    def visible_to(self, user):
        if user.can_see_all:
            return self
        return self.filter(sales_rep=user)



class Client(models.Model):
    objects = ClientQuerySet.as_manager()
    first_name = models.CharField("nombre", max_length=150)
    last_name = models.CharField("apellidos", max_length=150)
    email = models.EmailField("correo electrónico", unique=True)
    phone = models.CharField("teléfono", max_length=20, blank=True, null=True)
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        verbose_name="empresa",
        related_name="clients",
    )
    sales_rep = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name="representante de ventas",
        related_name="clients",
        blank=True,
        null=True
    )
    notes = models.TextField("notas", blank=True, null=True)
    created_at = models.DateTimeField("fecha de creación", default=timezone.now)
    updated_at = models.DateTimeField("fecha de actualización", auto_now=True)

    class Meta:
        verbose_name = 'cliente'
        verbose_name_plural = 'clientes'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_absolute_url(self):
        return reverse('crm:client_detail', kwargs={'pk': self.pk})
    

class InteractionQuerySet(models.QuerySet):
    def visible_to(self, user):
        if user.can_see_all:
            return self
        return self.filter(user=user)

    

class Interaction(models.Model):
    class Kind(models.TextChoices):
        CALL = "call", "Llamada"
        MEETING = "meeting", "Reunión"
        EMAIL = "email", "Correo electrónico"
        OTHER = "other", "Otro"
        
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        verbose_name="cliente",
        related_name="interactions",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name="registrado por",
        related_name="interactions",
        null=True
    )
    kind = models.TextField("tipo", max_length=10, choices=Kind.choices, default=Kind.CALL)
    date = models.DateTimeField("fecha", default=timezone.now)
    created_at = models.DateTimeField("fecha de creación", default=timezone.now)
    notes = models.TextField("notas", blank=True)
    summary = models.TextField("resumen", max_length=500)
    objects = InteractionQuerySet.as_manager()

    class Meta:
        verbose_name = 'interacción'
        verbose_name_plural = 'interacciones'
        ordering = ['-date']

    def __str__(self):
        return f"{self.get_kind_display()} con {self.client} el {self.date:%d/%m/%Y}"
        
    def get_absolute_url(self):
        return self.client.get_absolute_url() + f"#interaction-{self.pk}"