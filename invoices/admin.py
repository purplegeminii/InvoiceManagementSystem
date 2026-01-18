from django.contrib import admin
from .models import *

# Register your models here.

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone']

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone']
    search_fields = ['name', 'email']

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'customer', 'date_created', 'date_due', 'status', 'total']
    list_filter = ['status', 'date_created']
    search_fields = ['invoice_number', 'customer__name']
    inlines = [InvoiceItemInline]

@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ['description', 'invoice', 'quantity', 'unit_price', 'total']