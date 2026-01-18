from django import forms
from django.forms import inlineformset_factory
from .models import Invoice, InvoiceItem

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['invoice_number', 'company', 'customer', 'date_due', 
                  'discount_amount', 'shipping_amount', 'status', 'notes']
        widgets = {
            'date_due': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['description', 'quantity', 'unit_price']

InvoiceItemFormSet = inlineformset_factory(
    Invoice, 
    InvoiceItem, 
    form=InvoiceItemForm,
    extra=3, 
    can_delete=True
)
