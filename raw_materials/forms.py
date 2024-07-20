from django import forms
from django.forms import DateInput
from .models import PurchaseOrder, PurchaseOrderLine, RawMaterial

class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['code', 'supplier', 'date', 'estimated_delivery_date', 'state']
        
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
            'estimated_delivery_date': DateInput(attrs={'type': 'date'}),
        }

class PurchaseOrderLineForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderLine
        fields = ['raw_material', 'quantity', 'price']
        
    def __init__(self, *args, **kwargs):
        supplier = kwargs.pop('supplier', None)
        super().__init__(*args, **kwargs)
        if supplier:
            self.fields['raw_material'].queryset = RawMaterial.objects.filter(suppliers=supplier)
        # self.fields['raw_material'].queryset = RawMaterial.objects.none()
        # self.fields['price'].widget.attrs['readonly'] = False