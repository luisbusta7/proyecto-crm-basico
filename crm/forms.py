from django import forms
from .models import Client

class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
                if isinstance(field.widget, forms.Select):
                    field.widget.attrs["class"] = "form-select"
                else:
                    field.widget.attrs["class"] = "form-control"

class ClientForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'email', 'phone', 'company', 'sales_rep', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4}),
        }