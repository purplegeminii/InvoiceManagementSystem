from invoices.models import Company, Customer, Invoice, InvoiceItem
from datetime import date, timedelta

# Create company
company = Company.objects.create(
    name="Tech Solutions Inc.",
    address="123 Business Street\nNew York, NY 10001",
    phone="555-123-4567",
    email="info@techsolutions.com"
)

# Create customer
customer = Customer.objects.create(
    name="ABC Corporation",
    email="contact@abc.com",
    phone="555-987-6543",
    address="456 Client Avenue\nLos Angeles, CA 90001"
)

# Create invoice
invoice = Invoice.objects.create(
    invoice_number="INV-001",
    company=company,
    customer=customer,
    date_due=date.today() + timedelta(days=30),
    discount_amount=50.00,
    shipping_amount=25.00,
    status='sent'
)

# Create invoice items
InvoiceItem.objects.create(
    invoice=invoice,
    description="Web Development Service",
    quantity=10,
    unit_price=150.00
)

InvoiceItem.objects.create(
    invoice=invoice,
    description="SEO Optimization",
    quantity=5,
    unit_price=200.00
)

print("Sample data created successfully!")