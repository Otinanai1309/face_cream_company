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
    is_connected_to_order = forms.BooleanField(required=False, label="Connected to Purchase Order?")
    
    class Meta:
        model = PurchaseInvoice
        fields = ['code', 'supplier', 'purchase_order_code', 'date_of_invoice']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['purchase_order_code'].queryset = PurchaseOrder.objects.filter(state__in=['pending', 'partial_pending'])
        self.fields['purchase_order_code'].required = False

    def clean(self):
        cleaned_data = super().clean()
        is_connected = cleaned_data.get('is_connected_to_order')
        purchase_order = cleaned_data.get('purchase_order_code')
        
        if is_connected and not purchase_order:
            raise forms.ValidationError("Please select a purchase order.")
        elif not is_connected:
            cleaned_data['purchase_order_code'] = None
        
        return cleaned_data


class PurchaseInvoiceLineForm(forms.ModelForm):
    class Meta:
        model = PurchaseInvoiceLine
        fields = ['raw_material', 'quantity', 'price_per_unit']
        widgets = {
            'raw_material': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'price_per_unit': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'instance' in kwargs and kwargs['instance']:
            self.fields['raw_material'].queryset = RawMaterial.objects.filter(suppliers=kwargs['instance'].purchase_invoice.supplier)
