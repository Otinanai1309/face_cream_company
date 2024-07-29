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
    # code = models.CharField(max_length=20, unique=False, default=uuid.uuid4)

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
        if not self.code:
            self.code = str(uuid.uuid4())[:20]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.code} by {self.supplier.name}"

class PurchaseOrderLine(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE)
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    vat = models.DecimalField(max_digits=10, decimal_places=2, editable=False, null=True, blank=True)

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