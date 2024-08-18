from django.db import models
from decimal import Decimal
import uuid

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
        if self.is_connected_to_order:
            purchase_order = self.purchase_order_code
            purchase_order.status = 'invoiced'
            purchase_order.save()
        super().save(*args, **kwargs)

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
        super().save(*args, **kwargs)
        self.update_stock()

    def update_stock(self):
        for line in self.purchaseinvoiceline_set.all():
            line.raw_material.stock += line.quantity
            line.raw_material.save()
            
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

    def update_invoice_lines(self):
        for line in self.purchaseinvoiceline_set.all():
            line.raw_material.stock += line.quantity
            line.raw_material.save()
    
    def save(self, *args, **kwargs):
        print(f"Before setting cost_amount: {self.cost_amount}")
        # self.cost_amount = self.quantity * self.price_per_unit
        
        print(f"Before setting vat_amount: {self.vat_amount}")
        # self.vat_amount = self.cost_amount * self.raw_material.get_vat_rate()
        print(f"After setting vat_amount: {self.vat_amount}")
        
        print(f"Before updating raw_material stock: {self.raw_material.stock}")
        self.raw_material.stock += self.quantity
        print(f"After updating raw_material stock: {self.raw_material.stock}")
        
        self.raw_material.save()
        print("Raw material saved")
        
        super().save(*args, **kwargs)
        print("PurchaseInvoiceLine saved")
        