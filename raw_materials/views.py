# views.py
import json
from django import forms
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import TemplateView

from .models import PurchaseOrder, PurchaseOrderLine, PurchaseInvoice, PurchaseInvoiceLine
from .models import Supplier, RawMaterial
from .forms import PurchaseOrderForm, PurchaseOrderLineForm, PurchaseInvoiceForm, PurchaseInvoiceLineForm

from django.urls import reverse_lazy
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import SupplierSerializer, RawMaterialSerializer, PurchaseOrderSerializer, PurchaseOrderLineSerializer
from django.forms import formset_factory
from django.forms import inlineformset_factory

from django.http import JsonResponse

from decimal import Decimal
import logging

from django.db import IntegrityError
from django.db import transaction
from django.db.models import Sum
from django.core.exceptions import ValidationError

from django.urls import reverse

logger = logging.getLogger(__name__)

PurchaseOrderLineFormSet = inlineformset_factory(
    PurchaseOrder, 
    PurchaseOrderLine, 
    form=PurchaseOrderLineForm, 
    extra=1,
    can_delete=True
)

def get_raw_materials(request):
    supplier_id = request.GET.get('supplier_id')
    raw_materials = RawMaterial.objects.filter(suppliers__id=supplier_id).values('id', 'name', 'vat_category')
    raw_materials = [{'id': rm['id'], 'name': rm['name'], 'vat_rate': Decimal(rm['vat_category']) / 100} for rm in raw_materials]
    return JsonResponse(raw_materials, safe=False)

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

def get_raw_material_vat_rate(request):
    raw_material_id = request.GET.get('raw_material_id')
    if raw_material_id:
        try:
            raw_material = RawMaterial.objects.get(id=raw_material_id)
            return JsonResponse({'vat_rate': str(raw_material.get_vat_rate())})
        except RawMaterial.DoesNotExist:
            return JsonResponse({'error': 'Raw material not found'}, status=404)
    return JsonResponse({'error': 'No raw material ID provided'}, status=400)

def update_purchase_order_status(purchase_order, invoice):
    # Check if all items in the purchase order are fully invoiced
    order_lines = purchase_order.purchaseorderline_set.all()
    for line in order_lines:
        invoiced_quantity = PurchaseInvoiceLine.objects.filter(
            purchase_invoice__purchase_order_code=purchase_order,
            raw_material=line.raw_material
        ).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

        if invoiced_quantity < line.quantity:
            purchase_order.state = 'partial_pending'
            purchase_order.save()
            return

    # If we've made it here, all items are fully invoiced
    purchase_order.state = 'completed'
    purchase_order.save()

def get_purchase_orders(request):
    supplier_id = request.GET.get('supplier_id')
    purchase_orders = PurchaseOrder.objects.filter(supplier_id=supplier_id, state__in=['pending', 'partial_pending'])
    return JsonResponse(list(purchase_orders.values('id', 'code')), safe=False)

def get_purchase_order_lines(request):
    purchase_order_id = request.GET.get('purchase_order_id')
    purchase_order_lines = PurchaseOrderLine.objects.filter(
        purchase_order_id=purchase_order_id,
        state__in=['pending', 'partial']
    )
    lines_data = [
        {
            'id': line.id,
            'raw_material': line.raw_material.name,
            'raw_material_id': line.raw_material.id,  # Ensure this is included
            'quantity': line.quantity,
            'price_per_unit': str(line.price),
            'vat_rate': float(line.raw_material.get_vat_rate()),
            'remaining_quantity': line.quantity - line.invoiced_quantity
        }
        for line in purchase_order_lines
    ]
    return JsonResponse(lines_data, safe=False)

def update_purchase_order_line_status(order_line, invoiced_quantity):
    total_quantity = order_line.quantity
    previously_invoiced = order_line.invoiced_quantity
    new_total_invoiced = previously_invoiced + invoiced_quantity

    if new_total_invoiced >= total_quantity:
        order_line.state = 'fulfilled'
    elif new_total_invoiced > 0:
        order_line.state = 'partial'
    else:
        order_line.state = 'pending'

    order_line.invoiced_quantity = new_total_invoiced
    order_line.save()

def update_order_statuses(purchase_order_id):
    order = PurchaseOrder.objects.get(id=purchase_order_id)
    lines = order.purchaseorderline_set.all()
    all_fulfilled = True
    for line in lines:
        if line.invoiced_quantity >= line.quantity:
            line.state = 'fulfilled'
        else:
            line.state = 'partial'
            all_fulfilled = False
        line.save()
    order.state = 'completed' if all_fulfilled else 'partial_pending'
    order.save()
       
# @transaction.atomic
def purchase_invoice_create(request):
    if request.method == 'POST':
        logger.info("Received POST request for purchase invoice creation")
        form = PurchaseInvoiceForm(request.POST)
        if form.is_valid():
            logger.info("Form is valid")
            invoice = form.save(commit=False)
            purchase_order_id = request.POST.get('purchase_order_code')
            logger.info(f"Purchase order ID: {purchase_order_id}")
            if purchase_order_id:
                invoice.purchase_order_code_id = purchase_order_id
            invoice.save()
            logger.info(f"Invoice created with ID: {invoice.id}")

            invoice_lines = json.loads(request.POST.get('invoice_lines', '[]'))
            logger.info(f"Number of invoice lines: {len(invoice_lines)}")
            logger.info(f"invoice lines: {invoice_lines}")
            for line_data in invoice_lines:
                logger.debug(f"Processing line data: {line_data}")
                raw_material_id = line_data.get('raw_material')
                if raw_material_id:
                    try:
                        raw_material = RawMaterial.objects.get(id=raw_material_id)
                        logger.info(f"Raw material: {raw_material}")
                        quantity = Decimal(line_data['quantity'])
                        
                        invoice_line = PurchaseInvoiceLine.objects.create(
                            purchase_invoice=invoice,
                            raw_material=raw_material,
                            quantity=quantity,
                            price_per_unit=Decimal(line_data['price_per_unit'])
                        )
                        logger.info(f"Created invoice line: {invoice_line.id}")
                    
                        if purchase_order_id:
                            order_line = PurchaseOrderLine.objects.get(
                                id=line_data.get('order_line_id'),
                                purchase_order_id=purchase_order_id,
                                raw_material=raw_material
                            )
                            
                            if order_line:
                                order_line.invoiced_quantity += quantity
                                order_line.save()
                                logger.info(f"Updated order line: {order_line.id}")
                    except RawMaterial.DoesNotExist:
                        logger.error(f"Raw material with id {raw_material_id} does not exist")
                        return JsonResponse({'success': False, 'errors': f'Raw material with id {raw_material_id} does not exist'})
                    except PurchaseOrderLine.DoesNotExist:
                        logger.error(f"Purchase order line not found for raw material {raw_material_id}")
                        return JsonResponse({'success': False, 'errors': f'Purchase order line not found for raw material {raw_material_id}'})

            invoice.update_stock()
            logger.info("Updated raw material stock")

            if purchase_order_id:
                logger.info(f"Updating order statuses for order: {purchase_order_id}")
                update_order_statuses(purchase_order_id)

            logger.info("Purchase invoice creation completed successfully")
            return JsonResponse({
                'success': True,
                'redirect_url': reverse('purchase_invoice_detail', kwargs={'pk': invoice.pk})
            })
        else:
            logger.error(f"Form validation failed. Errors: {form.errors}")
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        logger.info("Received GET request for purchase invoice creation")
        form = PurchaseInvoiceForm()
    return render(request, 'raw_materials/purchase_invoice_create.html', {'form': form})

def get_supplier_raw_materials(request):
    supplier_id = request.GET.get('supplier_id')
    raw_materials = RawMaterial.objects.filter(suppliers__id=supplier_id)
    data = [{'id': rm.id, 'name': rm.name, 'vat_rate': float(rm.get_vat_rate())} for rm in raw_materials]
    return JsonResponse(data, safe=False)


def purchase_invoice_detail(request, pk):
    invoice = PurchaseInvoice.objects.get(pk=pk)
    return render(request, 'raw_materials/purchase_invoice_detail.html', {'invoice': invoice})

def purchase_invoice_add_line(request, pk):
    invoice = PurchaseInvoice.objects.get(pk=pk)
    if request.method == 'POST':
        form = PurchaseInvoiceLineForm(request.POST)
        if form.is_valid():
            line = form.save(commit=False)
            line.invoice = invoice
            line.save()
            return redirect('raw_materials/purchase_invoice_detail', pk=invoice.pk)
    else:
        form = PurchaseInvoiceLineForm()
    return render(request, 'raw_materials/purchase_invoice_add_line.html', {'form': form})

def home(request):
    return render(request, 'index.html')

class PurchaseInvoiceListView(ListView):
    model = PurchaseInvoice
    template_name = 'raw_materials/purchase_invoice_list.html'
    context_object_name = 'invoices'

class PurchaseInvoiceEditView(UpdateView):
    model = PurchaseInvoice
    form_class = PurchaseInvoiceForm
    template_name = 'raw_materials/purchase_invoice_edit.html'
    
    def get_success_url(self):
        return reverse_lazy('purchase_invoice_list')

class PurchaseInvoiceDeleteView(DeleteView):
    model = PurchaseInvoice
    success_url = reverse_lazy('purchase_invoice_list')
    template_name = 'raw_materials/purchase_invoice_confirm_delete.html'
    
class IndexView(TemplateView):
    template_name = "index.html"
    
"""def create_purchase_order(request):
    PurchaseOrderLineFormSet = formset_factory(PurchaseOrderLineForm, extra=1)
    if request.method == 'POST':
        logger.info(f"Received POST data: {request.POST}")
        # Rest of your view logic
        
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
    return render(request, 'raw_materials/purchaseorder_form.html', {'form': form, 'lines': formset})"""

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lines'] = self.object.purchaseorderline_set.all()
        context['total_cost'] = sum(line.cost for line in context['lines'])
        context['total_vat'] = sum(line.vat for line in context['lines'])
        return context

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
        print('lines', lines)
        with transaction.atomic():
            self.object = form.save()
            if lines.is_valid():
                for line_form in lines:
                    if line_form.cleaned_data and not line_form.cleaned_data.get('DELETE', False):
                        line = line_form.save(commit=False)
                        line.purchase_order = self.object
                        print('line', line, 'line.purchase')
                        line.save()
        return JsonResponse({'success': True, 'url': self.get_success_url()})



    def form_invalid(self, form):
        context = self.get_context_data()
        lines = context['lines']
        print('form invalid lines:', lines)
        form_errors = form.errors
        line_errors = lines.errors
        print('form_errors', form_errors, 'line_errors', line_errors)
        return JsonResponse({'success': False, 'form_errors': form_errors, 'line_errors': line_errors})

    def get_success_url(self):
        return '/api/purchase-orders/'

"""    def get_success_url(self):
        return reverse_lazy('purchaseorder_list')"""
    

class PurchaseOrderUpdateView(UpdateView):
    model = PurchaseOrder
    form_class = PurchaseOrderForm
    template_name = 'raw_materials/purchaseorder_update_form.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['lines'] = PurchaseOrderLineFormSet(
                self.request.POST, 
                instance=self.object,
                form_kwargs={'supplier': self.object.supplier}
            )
        else:
            data['lines'] = PurchaseOrderLineFormSet(
                instance=self.object,
                form_kwargs={'supplier': self.object.supplier}
            )
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        lines = context['lines']
        with transaction.atomic():
            self.object = form.save()
            if lines.is_valid():
                lines.instance = self.object
                lines.save()
            else:
                return self.form_invalid(form)
        return JsonResponse({'success': True, 'url': self.get_success_url()})

    def form_invalid(self, form):
        context = self.get_context_data()
        lines = context['lines']
        return JsonResponse({
            'success': False,
            'form_errors': form.errors,
            'line_errors': [form.errors for form in lines.forms if form.errors]
        })

         
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