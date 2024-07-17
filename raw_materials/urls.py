# raw_materials/urls.py
from django.urls import path, include
from .views import (
    SupplierListView, SupplierDetailView, SupplierCreateView, SupplierUpdateView, SupplierDeleteView,
    RawMaterialListView, RawMaterialDetailView, RawMaterialCreateView, RawMaterialUpdateView, RawMaterialDeleteView,
    PurchaseOrderListView, PurchaseOrderDetailView, PurchaseOrderCreateView, PurchaseOrderUpdateView, PurchaseOrderDeleteView,
    home,
)

from rest_framework.routers import DefaultRouter
from .views import SupplierViewSet, RawMaterialViewSet, PurchaseOrderViewSet, PurchaseOrderLineViewSet
from .views import get_raw_materials, update_raw_material_price, get_raw_material_price, get_raw_material_vat_rate
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
    
     # ... other url patterns ...
    path('purchase-order/create/', PurchaseOrderCreateView.as_view(), name='create_purchase_order'),
    
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

    path('purchaseorders/', PurchaseOrderListView.as_view(), name='purchaseorder_list'),
    path('purchaseorders/new/', PurchaseOrderCreateView.as_view(), name='purchaseorder_create'),
    path('purchaseorders/<int:pk>/', PurchaseOrderDetailView.as_view(), name='purchaseorder_detail'),
    path('purchaseorders/<int:pk>/update/', PurchaseOrderUpdateView.as_view(), name='purchaseorder_update'),
    path('purchaseorders/<int:pk>/delete/', PurchaseOrderDeleteView.as_view(), name='purchaseorder_delete'),
]