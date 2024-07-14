# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.forms import inlineformset_factory
from .models import PurchaseOrder, PurchaseOrderLine
from .models import Supplier, RawMaterial
from .forms import PurchaseOrderForm, PurchaseOrderLineForm
from django.urls import reverse_lazy
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import SupplierSerializer, RawMaterialSerializer, PurchaseOrderSerializer, PurchaseOrderLineSerializer
from django.forms import formset_factory

from django.http import JsonResponse

def get_raw_materials(request):
    supplier_id = request.GET.get('supplier_id')
    print(f"Fetching raw materials for supplier ID: {supplier_id}")
    raw_materials = RawMaterial.objects.filter(suppliers__id=supplier_id).values('id', 'name')
    return JsonResponse(list(raw_materials), safe=False)

def get_raw_material_price(request):
    raw_material_id = request.GET.get('raw_material_id')
    raw_material = RawMaterial.objects.get(id=raw_material_id)
    return JsonResponse({'price': str(raw_material.price)})
def update_raw_material_price(request):
    if request.method == 'POST':
        raw_material_id = request.POST.get('raw_material_id')
        new_price = request.POST.get('new_price')
        raw_material = RawMaterial.objects.get(id=raw_material_id)
        raw_material.price = new_price
        raw_material.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

def home(request):
    return render(request, 'home.html')


def create_purchase_order(request):
    PurchaseOrderLineFormSet = formset_factory(PurchaseOrderLineForm, extra=1)
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        formset = PurchaseOrderLineFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            purchase_order = form.save()
            for line_form in formset:
                if line_form.cleaned_data:
                    line = line_form.save(commit=False)
                    line.purchase_order = purchase_order
                    line.save()
            return redirect('purchase_order_detail', pk=purchase_order.pk)
    else:
        form = PurchaseOrderForm()
        formset = PurchaseOrderLineFormSet()
    return render(request, 'raw_materials/purchaseorder_form.html', {'form': form, 'lines': formset})

# RawMaterial Views
class RawMaterialListView(ListView):
    model = RawMaterial
    template_name = 'raw_materials/rawmaterial_list.html'
    context_object_name = 'rawmaterials'
    
class RawMaterialDetailView(DetailView):
    model = RawMaterial
    template_name = 'raw_materials/rawmaterial_detail.html'
    context_object_name = 'rawmaterial'

class RawMaterialCreateView(CreateView):
    model = RawMaterial
    template_name = 'raw_materials/rawmaterial_form.html'
    fields = ['code', 'name', 'description', 'price', 'vat_category', 'stock', 'barcode', 'suppliers']
    
    def get_success_url(self):
        return reverse_lazy('rawmaterial_list')

class RawMaterialUpdateView(UpdateView):
    model = RawMaterial
    template_name = 'raw_materials/rawmaterial_form.html'
    fields = ['code', 'name', 'description', 'price', 'vat_category', 'stock', 'barcode', 'suppliers']
    
    def get_success_url(self):
        return reverse_lazy('rawmaterial_detail', kwargs={'pk': self.object.pk})

class RawMaterialDeleteView(DeleteView):
    model = RawMaterial
    template_name = 'raw_materials/rawmaterial_confirm_delete.html'
    success_url = reverse_lazy('rawmaterial_list')

class SupplierListView(ListView):
    model = Supplier
    template_name = 'raw_materials/supplier_list.html'
    context_object_name = 'suppliers'

class SupplierDetailView(DetailView):
    model = Supplier
    template_name = 'raw_materials/supplier_detail.html'
    context_object_name = 'supplier'

class SupplierCreateView(CreateView):
    model = Supplier
    template_name = 'raw_materials/supplier_form.html'
    fields = ['code', 'name', 'address', 'phone', 'mobile', 'email']
    
    def get_success_url(self):
        return reverse_lazy('supplier_list')

class SupplierUpdateView(UpdateView):
    model = Supplier
    template_name = 'raw_materials/supplier_form.html'
    fields = ['code', 'name', 'address', 'phone', 'mobile', 'email']
    
    def get_success_url(self):
        return reverse_lazy('supplier_detail', kwargs={'pk': self.object.pk})

class SupplierDeleteView(DeleteView):
    model = Supplier
    template_name = 'raw_materials/supplier_confirm_delete.html'
    success_url = reverse_lazy('supplier_list')

class PurchaseOrderListView(ListView):
    model = PurchaseOrder
    template_name = 'raw_materials/purchaseorder_list.html'
    context_object_name = 'purchaseorders'

class PurchaseOrderDetailView(DetailView):
    model = PurchaseOrder
    template_name = 'raw_materials/purchaseorder_detail.html'
    context_object_name = 'purchaseorder'

class PurchaseOrderCreateView(CreateView):
    model = PurchaseOrder
    form_class = PurchaseOrderForm
    template_name = 'raw_materials/purchaseorder_form.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['lines'] = inlineformset_factory(PurchaseOrder, PurchaseOrderLine, form=PurchaseOrderLineForm, extra=1)(self.request.POST)
        else:
            data['lines'] = inlineformset_factory(PurchaseOrder, PurchaseOrderLine, form=PurchaseOrderLineForm, extra=1)()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        lines = context['lines']
        self.object = form.save()
        if lines.is_valid():
            lines.instance = self.object
            lines.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('purchaseorder_list')
    
class PurchaseOrderUpdateView(UpdateView):
    model = PurchaseOrder
    form_class = PurchaseOrderForm
    template_name = 'raw_materials/purchaseorder_form.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['lines'] = inlineformset_factory(PurchaseOrder, PurchaseOrderLine, form=PurchaseOrderLineForm, extra=1)(self.request.POST, instance=self.object, form_kwargs={'supplier': self.object.supplier})
        else:
            data['lines'] = inlineformset_factory(PurchaseOrder, PurchaseOrderLine, form=PurchaseOrderLineForm, extra=1)(instance=self.object, form_kwargs={'supplier': self.object.supplier})
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        lines = context['lines']
        self.object = form.save()
        if lines.is_valid():
            lines.instance = self.object
            lines.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('purchaseorder_list')
        #return reverse_lazy('purchaseorder_detail', kwargs={'pk': self.object.pk})
    
class PurchaseOrderDeleteView(DeleteView):
    model = PurchaseOrder
    template_name = 'raw_materials/purchaseorder_confirm_delete.html'
    success_url = reverse_lazy('purchaseorder_list')
    
class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

class RawMaterialViewSet(viewsets.ModelViewSet):
    queryset = RawMaterial.objects.all()
    serializer_class = RawMaterialSerializer

    @action(detail=False, methods=['get'])
    def list_raw_materials(self, request):
        raw_materials = self.get_queryset()
        serializer = self.get_serializer(raw_materials, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def detail_raw_material(self, request, pk=None):
        raw_material = self.get_object()
        serializer = self.get_serializer(raw_material)
        return Response(serializer.data)

class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer

class PurchaseOrderLineViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrderLine.objects.all()
    serializer_class = PurchaseOrderLineSerializer