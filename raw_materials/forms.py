from django import forms
from django.forms import DateInput
from .models import PurchaseOrder, PurchaseOrderLine, RawMaterial
from django.core.validators import MinValueValidator

from .models import PurchaseInvoice, PurchaseInvoiceLine

class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['code', 'supplier', 'date', 'estimated_delivery_date', 'state']
        
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
            'estimated_delivery_date': DateInput(attrs={'type': 'date'}),
        }

class PurchaseOrderLineForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = PurchaseOrderLine
        fields = ['id', 'raw_material', 'quantity', 'price']

    def __init__(self, *args, **kwargs):
        from django.core.validators import MinValueValidator
        self.supplier = kwargs.pop('supplier', None)
        super().__init__(*args, **kwargs)

        self.fields['quantity'].validators.append(MinValueValidator(1))
        self.fields['price'].validators.append(MinValueValidator(0))

        if self.supplier:
            self.fields['raw_material'].queryset = RawMaterial.objects.filter(suppliers=self.supplier)
        elif self.instance and hasattr(self.instance, 'purchase_order') and self.instance.purchase_order:
            self.fields['raw_material'].queryset = RawMaterial.objects.filter(suppliers=self.instance.purchase_order.supplier)
        else:
            self.fields['raw_material'].queryset = RawMaterial.objects.none()

        # Make fields not required for the form (but keep the model validation)
        self.fields['raw_material'].required = False
        self.fields['quantity'].required = False
        self.fields['price'].required = False
        
class PurchaseInvoiceForm(forms.ModelForm):
    class Meta:
        model = PurchaseInvoice
        fields = ['code', 'supplier', 'purchase_order_code', 'date_of_invoice']
        widgets = {
            'date_of_invoice': forms.DateInput(attrs={'type': 'date'}),
        }

class PurchaseInvoiceLineForm(forms.ModelForm):
    class Meta:
        model = PurchaseInvoiceLine
        fields = ['purchase_invoice', 'raw_material', 'quantity', 'price_per_unit']