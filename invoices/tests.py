from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date, timedelta
from .models import Company, Customer, Invoice, InvoiceItem
from .forms import InvoiceForm, InvoiceItemForm


class CompanyModelTest(TestCase):
    """Test cases for the Company model"""
    
    def setUp(self):
        self.company = Company.objects.create(
            name="Test Company",
            address="123 Test St, Test City",
            phone="555-1234",
            email="test@company.com"
        )
    
    def test_company_creation(self):
        """Test that a company can be created successfully"""
        self.assertEqual(self.company.name, "Test Company")
        self.assertEqual(self.company.email, "test@company.com")
        self.assertTrue(isinstance(self.company, Company))
    
    def test_company_str_method(self):
        """Test the string representation of Company"""
        self.assertEqual(str(self.company), "Test Company")
    
    def test_company_verbose_name_plural(self):
        """Test the plural verbose name"""
        self.assertEqual(str(Company._meta.verbose_name_plural), "Companies")


class CustomerModelTest(TestCase):
    """Test cases for the Customer model"""
    
    def setUp(self):
        self.customer = Customer.objects.create(
            name="John Doe",
            email="john@example.com",
            phone="555-5678",
            address="456 Customer Ave"
        )
    
    def test_customer_creation(self):
        """Test that a customer can be created successfully"""
        self.assertEqual(self.customer.name, "John Doe")
        self.assertEqual(self.customer.email, "john@example.com")
        self.assertTrue(isinstance(self.customer, Customer))
    
    def test_customer_str_method(self):
        """Test the string representation of Customer"""
        self.assertEqual(str(self.customer), "John Doe")


class InvoiceModelTest(TestCase):
    """Test cases for the Invoice model"""
    
    def setUp(self):
        self.company = Company.objects.create(
            name="Test Company",
            address="123 Test St",
            phone="555-1234",
            email="test@company.com"
        )
        self.customer = Customer.objects.create(
            name="John Doe",
            email="john@example.com",
            phone="555-5678",
            address="456 Customer Ave"
        )
        self.invoice = Invoice.objects.create(
            invoice_number="INV-001",
            company=self.company,
            customer=self.customer,
            date_due=date.today() + timedelta(days=30),
            status='draft',
            discount_amount=Decimal('10.00'),
            shipping_amount=Decimal('5.00')
        )
    
    def test_invoice_creation(self):
        """Test that an invoice can be created successfully"""
        self.assertEqual(self.invoice.invoice_number, "INV-001")
        self.assertEqual(self.invoice.status, 'draft')
        self.assertTrue(isinstance(self.invoice, Invoice))
    
    def test_invoice_str_method(self):
        """Test the string representation of Invoice"""
        self.assertEqual(str(self.invoice), "Invoice INV-001")
    
    def test_invoice_unique_number(self):
        """Test that invoice numbers must be unique"""
        with self.assertRaises(Exception):
            Invoice.objects.create(
                invoice_number="INV-001",
                company=self.company,
                customer=self.customer,
                date_due=date.today() + timedelta(days=30)
            )
    
    def test_invoice_status_choices(self):
        """Test invoice status choices"""
        valid_statuses = ['draft', 'sent', 'paid', 'cancelled']
        for status in valid_statuses:
            self.invoice.status = status
            self.invoice.save()
            self.assertEqual(self.invoice.status, status)
    
    def test_invoice_subtotal_empty(self):
        """Test subtotal calculation with no items"""
        self.assertEqual(self.invoice.subtotal, 0)
    
    def test_invoice_subtotal_with_items(self):
        """Test subtotal calculation with items"""
        InvoiceItem.objects.create(
            invoice=self.invoice,
            description="Item 1",
            quantity=2,
            unit_price=Decimal('50.00')
        )
        InvoiceItem.objects.create(
            invoice=self.invoice,
            description="Item 2",
            quantity=1,
            unit_price=Decimal('30.00')
        )
        self.assertEqual(self.invoice.subtotal, Decimal('130.00'))
    
    def test_invoice_total_discount(self):
        """Test total discount property"""
        self.assertEqual(self.invoice.total_discount, Decimal('10.00'))
    
    def test_invoice_shipping_cost(self):
        """Test shipping cost property"""
        self.assertEqual(self.invoice.shipping_cost, Decimal('5.00'))
    
    def test_invoice_total_calculation(self):
        """Test total calculation (subtotal - discount + shipping)"""
        InvoiceItem.objects.create(
            invoice=self.invoice,
            description="Item 1",
            quantity=2,
            unit_price=Decimal('50.00')
        )
        # subtotal = 100, discount = 10, shipping = 5
        # total = 100 - 10 + 5 = 95
        self.assertEqual(self.invoice.total, Decimal('95.00'))
    
    def test_invoice_negative_discount_validation(self):
        """Test that negative discount amounts are not allowed"""
        invoice = Invoice(
            invoice_number="INV-002",
            company=self.company,
            customer=self.customer,
            date_due=date.today() + timedelta(days=30),
            discount_amount=Decimal('-10.00')
        )
        with self.assertRaises(ValidationError):
            invoice.full_clean()
    
    def test_invoice_negative_shipping_validation(self):
        """Test that negative shipping amounts are not allowed"""
        invoice = Invoice(
            invoice_number="INV-003",
            company=self.company,
            customer=self.customer,
            date_due=date.today() + timedelta(days=30),
            shipping_amount=Decimal('-5.00')
        )
        with self.assertRaises(ValidationError):
            invoice.full_clean()


class InvoiceItemModelTest(TestCase):
    """Test cases for the InvoiceItem model"""
    
    def setUp(self):
        self.company = Company.objects.create(
            name="Test Company",
            address="123 Test St",
            phone="555-1234",
            email="test@company.com"
        )
        self.customer = Customer.objects.create(
            name="John Doe",
            email="john@example.com",
            phone="555-5678",
            address="456 Customer Ave"
        )
        self.invoice = Invoice.objects.create(
            invoice_number="INV-001",
            company=self.company,
            customer=self.customer,
            date_due=date.today() + timedelta(days=30)
        )
        self.item = InvoiceItem.objects.create(
            invoice=self.invoice,
            description="Test Item",
            quantity=3,
            unit_price=Decimal('25.00')
        )
    
    def test_invoice_item_creation(self):
        """Test that an invoice item can be created successfully"""
        self.assertEqual(self.item.description, "Test Item")
        self.assertEqual(self.item.quantity, 3)
        self.assertEqual(self.item.unit_price, Decimal('25.00'))
        self.assertTrue(isinstance(self.item, InvoiceItem))
    
    def test_invoice_item_str_method(self):
        """Test the string representation of InvoiceItem"""
        self.assertEqual(str(self.item), "Test Item - INV-001")
    
    def test_invoice_item_total(self):
        """Test total calculation (quantity * unit_price)"""
        self.assertEqual(self.item.total, Decimal('75.00'))
    
    def test_invoice_item_quantity_validation(self):
        """Test that quantity must be at least 1"""
        item = InvoiceItem(
            invoice=self.invoice,
            description="Invalid Item",
            quantity=0,
            unit_price=Decimal('10.00')
        )
        with self.assertRaises(ValidationError):
            item.full_clean()
    
    def test_invoice_item_negative_price_validation(self):
        """Test that unit price must be positive"""
        item = InvoiceItem(
            invoice=self.invoice,
            description="Invalid Item",
            quantity=1,
            unit_price=Decimal('0.00')
        )
        with self.assertRaises(ValidationError):
            item.full_clean()
    
    def test_invoice_item_cascade_delete(self):
        """Test that items are deleted when invoice is deleted"""
        item_id = self.item.id
        self.invoice.delete()
        self.assertFalse(InvoiceItem.objects.filter(id=item_id).exists())


class InvoiceFormTest(TestCase):
    """Test cases for the InvoiceForm"""
    
    def setUp(self):
        self.company = Company.objects.create(
            name="Test Company",
            address="123 Test St",
            phone="555-1234",
            email="test@company.com"
        )
        self.customer = Customer.objects.create(
            name="John Doe",
            email="john@example.com",
            phone="555-5678",
            address="456 Customer Ave"
        )
    
    def test_invoice_form_valid_data(self):
        """Test form with valid data"""
        form_data = {
            'invoice_number': 'INV-001',
            'company': self.company.id,
            'customer': self.customer.id,
            'date_due': date.today() + timedelta(days=30),
            'discount_amount': Decimal('10.00'),
            'shipping_amount': Decimal('5.00'),
            'status': 'draft',
            'notes': 'Test notes'
        }
        form = InvoiceForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_invoice_form_missing_required_fields(self):
        """Test form with missing required fields"""
        form = InvoiceForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('invoice_number', form.errors)
        self.assertIn('company', form.errors)
        self.assertIn('customer', form.errors)


class InvoiceItemFormTest(TestCase):
    """Test cases for the InvoiceItemForm"""
    
    def test_invoice_item_form_valid_data(self):
        """Test form with valid data"""
        form_data = {
            'description': 'Test Item',
            'quantity': 5,
            'unit_price': Decimal('20.00')
        }
        form = InvoiceItemForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_invoice_item_form_missing_fields(self):
        """Test form with missing required fields"""
        form = InvoiceItemForm(data={})
        self.assertFalse(form.is_valid())


class InvoiceViewsTest(TestCase):
    """Test cases for invoice views"""
    
    def setUp(self):
        self.client = Client()
        self.company = Company.objects.create(
            name="Test Company",
            address="123 Test St",
            phone="555-1234",
            email="test@company.com"
        )
        self.customer = Customer.objects.create(
            name="John Doe",
            email="john@example.com",
            phone="555-5678",
            address="456 Customer Ave"
        )
        self.invoice = Invoice.objects.create(
            invoice_number="INV-001",
            company=self.company,
            customer=self.customer,
            date_due=date.today() + timedelta(days=30),
            status='draft'
        )
        self.item = InvoiceItem.objects.create(
            invoice=self.invoice,
            description="Test Item",
            quantity=2,
            unit_price=Decimal('50.00')
        )
    
    def test_invoice_list_view(self):
        """Test invoice list view"""
        response = self.client.get(reverse('invoice_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'invoices/invoice_list.html')
        self.assertContains(response, 'INV-001')
    
    def test_invoice_list_search(self):
        """Test invoice list search functionality"""
        response = self.client.get(reverse('invoice_list'), {'search': 'INV-001'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'INV-001')
    
    def test_invoice_list_filter_by_status(self):
        """Test invoice list filter by status"""
        response = self.client.get(reverse('invoice_list'), {'status': 'draft'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'INV-001')
    
    def test_invoice_detail_view(self):
        """Test invoice detail view"""
        response = self.client.get(reverse('invoice_detail', kwargs={'pk': self.invoice.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'invoices/invoice_detail.html')
        self.assertContains(response, 'INV-001')
        self.assertContains(response, 'Test Item')
    
    def test_invoice_detail_view_404(self):
        """Test invoice detail view with non-existent invoice"""
        response = self.client.get(reverse('invoice_detail', kwargs={'pk': 9999}))
        self.assertEqual(response.status_code, 404)
    
    def test_invoice_create_view_get(self):
        """Test GET request to invoice create view"""
        response = self.client.get(reverse('invoice_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'invoices/invoice_form.html')
        self.assertIn('form', response.context)
        self.assertIn('formset', response.context)
    
    def test_invoice_create_view_post_valid(self):
        """Test POST request to create an invoice with valid data"""
        form_data = {
            'invoice_number': 'INV-002',
            'company': self.company.id,
            'customer': self.customer.id,
            'date_due': date.today() + timedelta(days=30),
            'discount_amount': '0',
            'shipping_amount': '0',
            'status': 'draft',
            'notes': '',
            # Formset management form
            'items-TOTAL_FORMS': '1',
            'items-INITIAL_FORMS': '0',
            'items-MIN_NUM_FORMS': '0',
            'items-MAX_NUM_FORMS': '1000',
            # First item
            'items-0-description': 'New Item',
            'items-0-quantity': '1',
            'items-0-unit_price': '100.00',
        }
        response = self.client.post(reverse('invoice_create'), data=form_data)
        self.assertEqual(Invoice.objects.count(), 2)
        new_invoice = Invoice.objects.get(invoice_number='INV-002')
        self.assertRedirects(response, reverse('invoice_detail', kwargs={'pk': new_invoice.pk}))
    
    def test_invoice_update_view_get(self):
        """Test GET request to invoice update view"""
        response = self.client.get(reverse('invoice_update', kwargs={'pk': self.invoice.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'invoices/invoice_form.html')
        self.assertIn('form', response.context)
        self.assertIn('formset', response.context)
    
    def test_invoice_update_view_post_valid(self):
        """Test POST request to update an invoice with valid data"""
        form_data = {
            'invoice_number': 'INV-001-UPDATED',
            'company': self.company.id,
            'customer': self.customer.id,
            'date_due': date.today() + timedelta(days=30),
            'discount_amount': '5.00',
            'shipping_amount': '10.00',
            'status': 'sent',
            'notes': 'Updated notes',
            # Formset management form
            'items-TOTAL_FORMS': '1',
            'items-INITIAL_FORMS': '1',
            'items-MIN_NUM_FORMS': '0',
            'items-MAX_NUM_FORMS': '1000',
            # Existing item
            'items-0-id': self.item.id,
            'items-0-description': 'Updated Item',
            'items-0-quantity': '3',
            'items-0-unit_price': '75.00',
        }
        response = self.client.post(reverse('invoice_update', kwargs={'pk': self.invoice.pk}), data=form_data)
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.invoice_number, 'INV-001-UPDATED')
        self.assertEqual(self.invoice.status, 'sent')
        self.assertRedirects(response, reverse('invoice_detail', kwargs={'pk': self.invoice.pk}))
    
    def test_invoice_delete_view_get(self):
        """Test GET request to invoice delete view"""
        response = self.client.get(reverse('invoice_delete', kwargs={'pk': self.invoice.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'invoices/invoice_confirm_delete.html')
    
    def test_invoice_delete_view_post(self):
        """Test POST request to delete an invoice"""
        invoice_pk = self.invoice.pk
        response = self.client.post(reverse('invoice_delete', kwargs={'pk': invoice_pk}))
        self.assertEqual(Invoice.objects.filter(pk=invoice_pk).count(), 0)
        self.assertRedirects(response, reverse('invoice_list'))
    
    def test_invoice_pdf_view(self):
        """Test invoice PDF generation view"""
        response = self.client.get(reverse('invoice_pdf', kwargs={'pk': self.invoice.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('Invoice_INV-001.pdf', response['Content-Disposition'])
    
    def test_invoice_pdf_download(self):
        """Test invoice PDF download"""
        response = self.client.get(reverse('invoice_pdf', kwargs={'pk': self.invoice.pk}) + '?download=1')
        self.assertEqual(response.status_code, 200)
        self.assertIn('attachment', response['Content-Disposition'])
    
    def test_invoice_pdf_view_404(self):
        """Test PDF generation for non-existent invoice"""
        response = self.client.get(reverse('invoice_pdf', kwargs={'pk': 9999}))
        self.assertEqual(response.status_code, 404)

