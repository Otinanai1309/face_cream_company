# raw_materials/urls.py
from django.urls import path, include
from .views import (
    SupplierListView, SupplierDetailView, SupplierCreateView, SupplierUpdateView, SupplierDeleteView,
    RawMaterialListView, RawMaterialDetailView, RawMaterialCreateView, RawMaterialUpdateView, RawMaterialDeleteView,
    PurchaseOrderListView, PurchaseOrderDetailView, PurchaseOrderCreateView, PurchaseOrderUpdateView, PurchaseOrderDeleteView,
    home, IndexView
    )

from rest_framework.routers import DefaultRouter
from .views import SupplierViewSet, RawMaterialViewSet, PurchaseOrderViewSet, PurchaseOrderLineViewSet
from .views import get_raw_materials, update_raw_material_price, get_raw_material_price, get_raw_material_vat_rate
from .views import purchase_invoice_create, purchase_invoice_detail, purchase_invoice_add_line, get_purchase_orders, get_purchase_order_lines, get_supplier_raw_materials
from .views import PurchaseInvoiceListView, PurchaseInvoiceEditView, PurchaseInvoiceDeleteView, update_invoiced_quantities

from django.views.generic import TemplateView
from django.contrib import admin

router = DefaultRouter()
router.register(r'api/suppliers', SupplierViewSet)
router.register(r'api/rawmaterials', RawMaterialViewSet)
router.register(r'api/purchaseorders', PurchaseOrderViewSet)
router.register(r'api/purchaseorderlines', PurchaseOrderLineViewSet)


urlpatterns = [
    path('', home, name='home'),
        
    path('', include(router.urls)),
    
    # ... existing patterns ...
    path('get-raw-materials/', get_raw_materials, name='get_raw_materials'),
    path('update-raw-material-price/', update_raw_material_price, name='update_raw_material_price'),
    path('get-raw-material-price/', get_raw_material_price, name='get_raw_material_price'),
    path('api/get-raw-material-vat-rate/', get_raw_material_vat_rate, name='get_raw_material_vat_rate'),

    
    path('suppliers/', SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/new/', SupplierCreateView.as_view(), name='supplier_create'),
    path('suppliers/<int:pk>/', SupplierDetailView.as_view(), name='supplier_detail'),
    path('suppliers/<int:pk>/update/', SupplierUpdateView.as_view(), name='supplier_update'),
    path('suppliers/<int:pk>/delete/', SupplierDeleteView.as_view(), name='supplier_delete'),

    path('rawmaterials/', RawMaterialListView.as_view(), name='rawmaterial_list'),
    path('rawmaterials/<int:pk>/', RawMaterialDetailView.as_view(), name='rawmaterial_detail'),
    path('rawmaterials/create/', RawMaterialCreateView.as_view(), name='rawmaterial_create'),
    path('rawmaterials/<int:pk>/update/', RawMaterialUpdateView.as_view(), name='rawmaterial_update'),
    path('rawmaterials/<int:pk>/delete/', RawMaterialDeleteView.as_view(), name='rawmaterial_delete'),

    path('purchase-orders/', PurchaseOrderListView.as_view(), name='purchaseorder_list'),
    path('purchase-orders/create/', PurchaseOrderCreateView.as_view(), name='create_purchase_order'),
    # path('purchaseorders/new/', PurchaseOrderCreateView.as_view(), name='purchaseorder_create'),
    path('purchase-orders/<int:pk>/', PurchaseOrderDetailView.as_view(), name='purchaseorder_detail'),
    path('purchase-orders/<int:pk>/update/', PurchaseOrderUpdateView.as_view(), name='purchaseorder_update'),
    path('purchase-orders/<int:pk>/delete/', PurchaseOrderDeleteView.as_view(), name='purchaseorder_delete'),
    
    path('get-purchase-orders/', get_purchase_orders, name='get_purchase_orders'),
    path('get-purchase-order-lines/', get_purchase_order_lines, name='get_purchase_order_lines'),
   
    path('purchase-invoice/create/', purchase_invoice_create, name='purchase_invoice_create'),
    path('purchase-invoice/<pk>/', purchase_invoice_detail, name='purchase_invoice_detail'),
    path('purchase-invoice/<int:pk>/line/', purchase_invoice_add_line, name='purchase_invoice_add_line'),
    path('purchase-invoice/line/', purchase_invoice_add_line, name='purchase_invoice_add_line_no_pk'),
    path('get-supplier-raw-materials/', get_supplier_raw_materials, name='get_supplier_raw_materials'),
    path('purchase-invoice/', PurchaseInvoiceListView.as_view(), name='purchase_invoice_list'),
    path('purchase-invoice/<int:pk>/edit/', PurchaseInvoiceEditView.as_view(), name='purchase_invoice_edit'),
    path('purchase-invoice/<int:pk>/delete/', PurchaseInvoiceDeleteView.as_view(), name='purchase_invoice_delete'),
    path('api/update-invoiced-quantities/', update_invoiced_quantities, name='update_invoiced_quantities'),
]