from django.db import models
from decimal import Decimal
import uuid

from django.db.models import Sum

from django.db import transaction

class Supplier(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    mobile = models.CharField(max_length=15)
    email = models.EmailField()

    def __str__(self):
        return self.name

class RawMaterial(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    vat_category = models.CharField(max_length=50)
    stock = models.IntegerField()
    barcode = models.CharField(max_length=50)
    suppliers = models.ManyToManyField(Supplier)

    def get_vat_rate(self):
        return Decimal(self.vat_category) / Decimal(100)
    
    def __str__(self):
        return self.name

class PurchaseOrder(models.Model):
    ORDER_STATES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('partial_pending', 'Partial Pending'),
    ]
    code = models.CharField(max_length=20, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    date = models.DateField()
    estimated_delivery_date = models.DateField()
    state = models.CharField(max_length=20, choices=ORDER_STATES, default='pending')
            
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
    
    def update_order_state(self):
        all_lines_fulfilled = all(line.state == 'fulfilled' for line in self.purchaseorderline_set.all())
        if all_lines_fulfilled:
            self.state = 'completed'
        else:
            self.state = 'partial_pending' if any(line.state == 'partial' for line in self.purchaseorderline_set.all()) else 'pending'
        self.save()
        

    def __str__(self):
        return f"Order {self.code} by {self.supplier.name}"

class PurchaseOrderLine(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE)
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    vat = models.DecimalField(max_digits=10, decimal_places=2, editable=False, null=True, blank=True)
    invoiced_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    STATE_CHOICES = [
        ('pending', 'Pending'),
        ('partial', 'Partially Fulfilled'),
        ('fulfilled', 'Fulfilled'),
    ]
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='pending')

    @property
    def cost(self):
        if self.quantity is not None and self.price is not None:
            return self.quantity * self.price
        return None

    def save(self, *args, **kwargs):
        if self.cost is not None:
            vat_rate = Decimal(self.raw_material.vat_category.split()[0]) / 100
            self.vat = self.cost * vat_rate
        else:
            self.vat = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Line for {self.raw_material.name} in order {self.purchase_order.code}"
    

class PurchaseInvoice(models.Model):
    code = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    purchase_order_code = models.ForeignKey(PurchaseOrder, null=True, blank=True, on_delete=models.SET_NULL)
    date_of_invoice = models.DateField()

    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Check if the instance is new (has no primary key)
        super().save(*args, **kwargs)  # Save the instance first
        if is_new:
            print(f"update stock on create from save model is called for {self.code}")
            self.update_stock_on_create()
        else:
            print(f"update stock on update from save model is called for {self.code}")
            self.update_stock_on_update()  # Custom stock update logic for updates

    def is_connected_to_order(self):
        return self.purchase_order_code is not None
    
    def update_stock_on_create(self):
        lines = self.purchaseinvoiceline_set.all()
        print(f"Lines associated with invoice {self.code}: {list(lines)}")
        for line in lines:
            print(f"inside update stock on create for {self.code}")
            print(f"stock before update for line {line.order_line} is {line.raw_material.stock}")
            line.raw_material.stock += line.quantity
            print(f"stock after update for line {line.order_line} is {line.raw_material.stock}")
            line.raw_material.save()
            print(f"{line.raw_material} saved")
            if line.order_line:
                line.order_line.invoiced_quantity += line.quantity
                line.order_line.save()
                self.update_order_line_state(line.order_line)

    def update_stock_on_update(self):
        original_invoice = PurchaseInvoice.objects.get(pk=self.pk)
        original_lines = original_invoice.purchaseinvoiceline_set.all()
        updated_lines = self.purchaseinvoiceline_set.all()

        # Update stock based on changes
        stock_changes = self.calculate_stock_changes(original_lines, updated_lines)
        for raw_material_id, quantity_change in stock_changes.items():
            raw_material = RawMaterial.objects.get(id=raw_material_id)
            raw_material.stock += quantity_change
            raw_material.save()

        # Recalculate invoiced quantities for all related order lines
        affected_order_lines = set(line.order_line for line in updated_lines if line.order_line)

        for order_line in affected_order_lines:
            # Recompute invoiced quantity directly from the database
            summed_invoiced_quantity = PurchaseInvoiceLine.objects.filter(order_line=order_line).aggregate(total_invoiced=Sum('quantity'))['total_invoiced'] or 0

            print(f"Recalculating: Order Line ID: {order_line.id}, Summed Invoiced Quantity: {summed_invoiced_quantity}")
            order_line.invoiced_quantity = summed_invoiced_quantity
            order_line.save()

            # Update the state based on the new invoiced quantity
            self.update_order_line_state(order_line)

    def update_order_line_state(self, order_line):
        print(f"Order Line ID: {order_line.id}, Invoiced Quantity: {order_line.invoiced_quantity}, Order Quantity: {order_line.quantity}")
        if order_line.invoiced_quantity >= order_line.quantity:
            order_line.state = 'fulfilled'
        elif order_line.invoiced_quantity > 0:
            order_line.state = 'partial'
        else:
            order_line.state = 'pending'
        order_line.save()
        print(f"Updated State: {order_line.state}")
        
        # Update the main order state
        if order_line.purchase_order:
            order_line.purchase_order.update_order_state()



    def calculate_stock_changes(self, original_lines, updated_lines):
        """ Helper function to calculate stock changes based on original and updated lines. """
        quantity_changes = {}

        for original_line in original_lines:
            quantity_changes[original_line.raw_material.id] = quantity_changes.get(original_line.raw_material.id, 0) - original_line.quantity

        for updated_line in updated_lines:
            quantity_changes[updated_line.raw_material.id] = quantity_changes.get(updated_line.raw_material.id, 0) + updated_line.quantity

        return quantity_changes


    def __str__(self):
        return f"Purchase Invoice #{self.code}"

    
class PurchaseInvoiceLine(models.Model):
    purchase_invoice = models.ForeignKey(PurchaseInvoice, on_delete=models.CASCADE)
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    vat = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    order_line = models.ForeignKey(PurchaseOrderLine, null=True, blank=True, on_delete=models.SET_NULL)

    @property
    def cost_amount(self):
        if self.quantity is not None and self.price_per_unit is not None:
            return self.quantity * self.price_per_unit
        return None

    @property
    def vat_amount(self):
        if self.cost_amount is not None:
            return self.cost_amount * self.raw_material.get_vat_rate()
        return None

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
                
        print("PurchaseInvoiceLine saved")
        