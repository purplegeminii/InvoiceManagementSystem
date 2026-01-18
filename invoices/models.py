from django.db import models
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

# Create your models here.


class Company(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    
    class Meta:
        verbose_name_plural = "Companies"
    
    def __str__(self):
        return self.name

class Customer(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    
    def __str__(self):
        return self.name

class Invoice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]
    
    invoice_number = models.CharField(max_length=50, unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date_created = models.DateField(auto_now_add=True)
    date_due = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Invoice {self.invoice_number}"
    
    @property
    def subtotal(self):
        return sum(item.total for item in self.items.all())
    
    @property
    def total_discount(self):
        return self.discount_amount or Decimal('0.00')
    
    @property
    def shipping_cost(self):
        return self.shipping_amount or Decimal('0.00')
    
    @property
    def total(self):
        return self.subtotal - self.total_discount + self.shipping_cost
    
    discount_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    shipping_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))]
    )

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    def __str__(self):
        return f"{self.description} - {self.invoice.invoice_number}"
    
    @property
    def total(self):
        return self.quantity * self.unit_price