from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

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


class Client(models.Model):
    first_name = models.CharField("nombre", max_length=150)
    last_name = models.CharField("apellido", max_length=150)
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
    

