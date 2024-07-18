from django import forms
from django.forms import DateInput
from .models import PurchaseOrder, PurchaseOrderLine, RawMaterial
from django.forms import inlineformset_factory

class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['code', 'supplier', 'date', 'estimated_delivery_date', 'state']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'estimated_delivery_date': forms.DateInput(attrs={'type': 'date'}),
        }


class PurchaseOrderLineForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderLine
        fields = ['raw_material', 'quantity', 'price']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'instance' in kwargs and kwargs['instance']:
            self.fields['raw_material'].queryset = RawMaterial.objects.all()
        self.fields['price'].widget.attrs['readonly'] = False

PurchaseOrderLineFormSet = inlineformset_factory(
    PurchaseOrder, PurchaseOrderLine, form=PurchaseOrderLineForm, extra=1
)