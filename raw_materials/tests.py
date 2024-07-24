from django.test import TestCase
from django.urls import reverse
from .models import PurchaseOrder, PurchaseOrderLine, RawMaterial, Supplier
from raw_materials.forms import PurchaseOrderLineForm
import json

# Create your tests here.

class CreatePurchaseOrderViewTestCase(TestCase):
    def setUp(self):
        self.supplier = Supplier.objects.create(code='SUP001', name='Test Supplier')
        self.raw_material = RawMaterial.objects.create(
            code='RM001', name='Test Raw Material', price=10.0, vat_category='24', stock=100
        )

    def test_create_purchase_order_success(self):
        url = reverse('create_purchase_order')
        data = {
            'code': 'PO001',
            'supplier': self.supplier.pk,
            'date': '2023-05-01',
            'estimated_delivery_date': '2023-05-15',
            'state': 'pending',
            'order_lines': [
                {
                    'raw_material_id': self.raw_material.pk,
                    'quantity': 10,
                    'price': self.raw_material.price
                }
            ]
        }
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 302)
        purchase_order = PurchaseOrder.objects.get(code='PO001')
        self.assertEqual(purchase_order.supplier, self.supplier)
        self.assertEqual(purchase_order.purchaseorderline_set.count(), 1)
        order_line = purchase_order.purchaseorderline_set.first()
        self.assertEqual(order_line.raw_material, self.raw_material)
        self.assertEqual(order_line.quantity, 10)
        self.assertEqual(order_line.price, self.raw_material.price)

    # Add more test cases for form validation errors, redirect behavior, etc.

class PurchaseOrderLineTestCase(TestCase):
    def setUp(self):
        self.supplier = Supplier.objects.create(
            code='SUP001',
            name='Test Supplier',
            address='Test Address',
            phone='1234567890',
            mobile='0987654321',
            email='<a href="mailto:supplier@example.com">supplier@example.com</a>'
        )
        self.raw_material = RawMaterial.objects.create(
            code='RM001',
            name='Test Raw Material',
            description='Test Description',
            price=10.00,
            vat_category='10%',
            stock=100,
            barcode='123456789012'
        )
        self.raw_material.suppliers.add(self.supplier)

        self.purchase_order = PurchaseOrder.objects.create(
            supplier=self.supplier,
            date='2023-05-01',
            estimated_delivery_date='2023-05-15'
        )

    def test_purchaseorderline_validation(self):
        # Test valid data
        valid_line = PurchaseOrderLine.objects.create(
            purchase_order=self.purchase_order,
            raw_material=self.raw_material,
            quantity=10,
            price=10.00
        )
        self.assertIsNotNone(valid_line)

        # Test invalid quantity
        with self.assertRaises(ValueError):
            PurchaseOrderLine.objects.create(
                purchase_order=self.purchase_order,
                raw_material=self.raw_material,
                quantity=0,
                price=10.00
            )

        # Test invalid price
        with self.assertRaises(ValueError):
            PurchaseOrderLine.objects.create(
                purchase_order=self.purchase_order,
                raw_material=self.raw_material,
                quantity=10,
                price=-5.00
            )